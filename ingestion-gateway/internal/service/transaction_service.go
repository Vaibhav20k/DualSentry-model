package service

import (
	"context"
	"fmt"
	"log"
	"time"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/features"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ml"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/idempotency"

	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"
)

type TransactionService struct {
	repository   repository.TransactionRepository
	anomalyRepo  repository.AnomalyRepository
	baselineRepo repository.BaselineRepository
	historyRepo  repository.HistoryRepository

	producer *kafka.Producer
	updater  *BaselineUpdater
	mlClient *ml.Client
}

func NewTransactionService(
	repo repository.TransactionRepository,
	anomalyRepo repository.AnomalyRepository,
	baselineRepo repository.BaselineRepository,
	historyRepo repository.HistoryRepository,
	producer *kafka.Producer,
	updater *BaselineUpdater,
	mlClient *ml.Client,
) *TransactionService {

	return &TransactionService{
		repository:   repo,
		anomalyRepo:  anomalyRepo,
		baselineRepo: baselineRepo,
		historyRepo:  historyRepo,
		producer:     producer,
		updater:      updater,
		mlClient:     mlClient,
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
	// Step 1: Persist transaction
	// ---------------------------------------------------------

	transactionID, err := s.repository.SaveTransaction(ctx, req)
	if err != nil {
		return nil, err
	}

	// ---------------------------------------------------------
	// Step 2: Update user baseline
	// ---------------------------------------------------------

	if s.updater != nil {
		if err := s.updater.UpdateBaseline(ctx, req.UserId); err != nil {
			return nil, err
		}
	}

	// ---------------------------------------------------------
	// Step 3: Build Transaction Event
	// ---------------------------------------------------------

	event := events.TransactionEvent{
		TransactionID: transactionID,
		UserID:        req.UserId,
		Timestamp:     req.Timestamp,

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
	// Step 4: Build Feature Vector
	// ---------------------------------------------------------

	vector := features.BuildFeatureVector(
		event,
		s.baselineRepo,
		s.historyRepo,
	)

	// ---------------------------------------------------------
	// Step 5: ML Prediction
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

	metrics.MLPredictionDuration.Observe(
		time.Since(predictionStart).Seconds(),
	)

	if err != nil {
		return nil, err
	}

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
	// Step 6: Persist Prediction
	// ---------------------------------------------------------

	anomalyType := "NORMAL"
	if prediction.Prediction {
		anomalyType = "FRAUD"
	}

	err = s.anomalyRepo.SavePrediction(
		ctx,
		transactionID,
		prediction.FraudProbability,
		anomalyType,
		"xgboost",
		"hi_li_small_v1",
		"",
	)
	if err != nil {
		return nil, err
	}

	event.FraudProbability = prediction.FraudProbability
	event.IsFraud = prediction.Prediction
	event.ModelName = "xgboost"
	event.ModelVersion = "hi_li_small_v1"
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