package service

import (
	"context"
	"fmt"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/decision"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/features"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/idempotency"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ml"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
	"log"
	"time"

	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"
)

type TransactionService struct {
	repository    repository.TransactionRepository
	anomalyRepo   repository.AnomalyRepository
	fraudPredRepo repository.FraudPredictionRepository
	baselineRepo  repository.BaselineRepository
	historyRepo   repository.HistoryRepository

	producer *kafka.Producer
	updater  *BaselineUpdater
	mlClient *ml.Client
}

func NewTransactionService(
	repo repository.TransactionRepository,
	anomalyRepo repository.AnomalyRepository,
	fraudPredRepo repository.FraudPredictionRepository,
	baselineRepo repository.BaselineRepository,
	historyRepo repository.HistoryRepository,
	producer *kafka.Producer,
	updater *BaselineUpdater,
	mlClient *ml.Client,
) *TransactionService {

	return &TransactionService{
		repository:    repo,
		anomalyRepo:   anomalyRepo,
		fraudPredRepo: fraudPredRepo,
		baselineRepo:  baselineRepo,
		historyRepo:   historyRepo,
		producer:      producer,
		updater:       updater,
		mlClient:      mlClient,
	}
}

func (s *TransactionService) SubmitTransaction(
	ctx context.Context,
	idempotencyKey string,
	req *pb.TransactionRequest,
) (*pb.TransactionResponse, error) {

	if idempotencyKey != "" {

		var cachedResponse pb.TransactionResponse

		found, err := idempotency.Exists(
			ctx,
			idempotencyKey,
			&cachedResponse,
		)

		if err != nil {
			return nil, err
		}

		if found {
			log.Printf(
				"Idempotency hit: %s",
				idempotencyKey,
			)

			return &cachedResponse, nil
		}
	}
	// ---------------------------------------------------------
	// Step 1: Build Transaction Event
	// ---------------------------------------------------------

	event := events.TransactionEvent{
		UserID:    req.UserId,
		Timestamp: req.Timestamp,

		Amount:          req.Amount,
		Currency:        req.Currency,
		TransactionType: req.TransactionType,

		PaymentMethod:     req.PaymentMethod,
		PaymentIdentifier: req.PaymentIdentifier,

		Merchant:         req.Merchant,
		MerchantCategory: req.MerchantCategory,
		ReceiverAccount:  req.ReceiverAccount,

		Location:  req.Location,
		IPAddress: req.IpAddress,
		DeviceID:  req.DeviceId,

		Status: "RECEIVED",
	}

	// ---------------------------------------------------------
	// Step 2: Build Feature Vector (from pre-transaction history)
	// ---------------------------------------------------------

	vector := features.BuildFeatureVector(
		event,
		s.baselineRepo,
		s.historyRepo,
	)

	// ---------------------------------------------------------
	// Step 3: ML Prediction
	// ---------------------------------------------------------

	predictionStart := time.Now()

	result, err := ml.PredictionBreaker.Execute(func() (interface{}, error) {
		return s.mlClient.Predict(ctx, vector)
	})

	metrics.MLPredictionDuration.Observe(
		time.Since(predictionStart).Seconds(),
	)

	if err != nil {
		return nil, err
	}

	prediction := result.(*ml.PredictionResponse)

	fmt.Printf(
		"\n==============================\n"+
			"ML Prediction\n"+
			"Probability : %.4f\n"+
			"Fraud       : %v\n"+
			"==============================\n",
		prediction.FraudProbability,
		prediction.Prediction,
	)

	// ---------------------------------------------------------
	// Step 4: Persist Raw Transaction
	// ---------------------------------------------------------

	transactionID, err := s.repository.SaveTransaction(ctx, req)
	if err != nil {
		return nil, err
	}
	event.TransactionID = transactionID

	// ---------------------------------------------------------
	// Step 5: Update User Baseline (post-transaction)
	// ---------------------------------------------------------

	if s.updater != nil {
		if err := s.updater.UpdateBaseline(ctx, req.UserId); err != nil {
			log.Printf("Warning: baseline update failed for user %s: %v", req.UserId, err)
		}
	}

	// ---------------------------------------------------------
	// Step 6: Persist Prediction
	// ---------------------------------------------------------

	decEngine := decision.NewEngine()
	dec := decEngine.Decide(prediction.FraudProbability)
	decisionStr := string(dec)

	isFraud := prediction.Prediction || dec == decision.Block

	err = s.anomalyRepo.SavePrediction(
		ctx,
		transactionID,
		prediction.FraudProbability,
		decisionStr,
		"xgboost",
		"2.0.0",
		"",
	)
	if err != nil {
		return nil, err
	}

	err = s.fraudPredRepo.SavePrediction(
		ctx,
		repository.FraudPrediction{
			TransactionID:    transactionID,
			UserID:           req.UserId,
			FraudProbability: prediction.FraudProbability,
			Confidence:       prediction.Confidence,
			Prediction:       isFraud,
			Decision:         decisionStr,
			Threshold:        prediction.Threshold,
			ModelVersion:     prediction.ModelVersion,
			RiskFlags:        vector.RiskFlags,
		},
	)
	if err != nil {
		return nil, err
	}

	event.FraudProbability = prediction.FraudProbability
	event.IsFraud = isFraud
	event.ModelName = "xgboost"
	event.ModelVersion = prediction.ModelVersion
	// ---------------------------------------------------------
	// Step 7: Publish Kafka Event
	// ---------------------------------------------------------

	log.Println("======================================")
	log.Println("Publishing transaction to Kafka...")
	log.Printf("Transaction ID : %s", transactionID)
	log.Printf("Fraud Score    : %.4f", event.FraudProbability)
	log.Printf("Is Fraud       : %v", event.IsFraud)

	if err := s.producer.PublishJSON(req.UserId, event); err != nil {
		log.Printf("❌ Kafka publish failed: %v", err)
		return nil, err
	}

	log.Println("✅ Kafka publish successful.")
	log.Println("======================================")

	// ---------------------------------------------------------
	// Step 8: Return Response
	// ---------------------------------------------------------

	response := &pb.TransactionResponse{
		TransactionId: transactionID,
		Status:        "RECEIVED",
		Message:       "Transaction stored successfully.",
	}

	if idempotencyKey != "" {

		if err := idempotency.Save(
			ctx,
			idempotencyKey,
			response,
		); err != nil {
			log.Printf(
				"Failed to cache idempotent response: %v",
				err,
			)
		}
	}

	return response, nil
}
