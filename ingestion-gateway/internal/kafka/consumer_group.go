package kafka

import (
	"context"
	"encoding/json"
	"log"

	"github.com/IBM/sarama"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/decision"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/features"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ml"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

type ConsumerGroupHandler struct {
	baselineRepo   repository.BaselineRepository
	historyRepo    repository.HistoryRepository
	predictionRepo repository.FraudPredictionRepository

	mlClient *ml.Client
	engine   *decision.Engine
}

func (h *ConsumerGroupHandler) Setup(
	sarama.ConsumerGroupSession,
) error {
	return nil
}

func (h *ConsumerGroupHandler) Cleanup(
	sarama.ConsumerGroupSession,
) error {
	return nil
}

func (h *ConsumerGroupHandler) ConsumeClaim(
	session sarama.ConsumerGroupSession,
	claim sarama.ConsumerGroupClaim,
) error {

	for message := range claim.Messages() {

		var event events.TransactionEvent

		if err := json.Unmarshal(message.Value, &event); err != nil {
			log.Printf("failed to decode event: %v", err)
			continue
		}

		featureVector := features.BuildFeatureVector(
			event,
			h.baselineRepo,
			h.historyRepo,
		)

		// Create CSV exporter
		csvExporter := features.NewCSVExporter(
			"../ml-anomaly-engine/data/feature_vectors/training_dataset.csv",
		)

		// Create feature pipeline
		pipeline := features.NewPipeline(csvExporter)

		// Export feature vector
		if err := pipeline.Process(featureVector); err != nil {
			log.Printf("failed to export feature vector: %v", err)
		}
		// ---------------------------------------------------------
		// Run ML Prediction
		// ---------------------------------------------------------

		prediction, err := h.mlClient.Predict(
			context.Background(),
			featureVector,
		)

		if err != nil {

			log.Printf(
				"ML prediction failed: %v",
				err,
			)

		} else {

			decisionResult := h.engine.Decide(
				prediction.FraudProbability,
			)

			err = h.predictionRepo.SavePrediction(
				context.Background(),
				repository.FraudPrediction{
					TransactionID:    featureVector.TransactionID,
					UserID:           featureVector.UserID,
					FraudProbability: prediction.FraudProbability,
					Confidence:       prediction.Confidence,
					Prediction:       prediction.Prediction,
					Decision:         string(decisionResult),
					Threshold:        prediction.Threshold,
					ModelVersion:     prediction.ModelVersion,
					RiskFlags:        featureVector.RiskFlags,
				},
			)

			if err != nil {
				log.Printf(
					"failed to save fraud prediction: %v",
					err,
				)
			} else {
				log.Println("Fraud prediction saved to PostgreSQL.")
			}

			log.Println("========== ML PREDICTION ==========")

			log.Printf(
				"Fraud Probability : %.4f",
				prediction.FraudProbability,
			)

			log.Printf(
				"Prediction        : %v",
				prediction.Prediction,
			)

			log.Printf(
				"Threshold         : %.4f",
				prediction.Threshold,
			)

			log.Printf(
				"Model Version     : %s",
				prediction.ModelVersion,
			)

			log.Printf(
				"Decision          : %s",
				decisionResult,
			)

			log.Println("===================================")
		}

		// Keep console logging
		featureJSON, _ := json.MarshalIndent(featureVector, "", "  ")

		log.Println("========== FEATURE VECTOR ==========")
		log.Println(string(featureJSON))
		log.Println("====================================")

		session.MarkMessage(message, "")
	}

	return nil
}

func (c *Consumer) ConsumeGroup() error {

	config := sarama.NewConfig()

	config.Version = sarama.V2_8_0_0

	group, err := sarama.NewConsumerGroup(
		[]string{"localhost:9092"},
		"fraud-detection-group",
		config,
	)
	if err != nil {
		return err
	}

	handler := &ConsumerGroupHandler{
		baselineRepo:   c.baselineRepo,
		historyRepo:    c.historyRepo,
		predictionRepo: c.predictionRepo,
		mlClient:       c.mlClient,
		engine:         c.engine,
	}

	log.Println("Joining consumer group...")

	for {
		log.Println("Waiting for messages...")

		err := group.Consume(
			context.Background(),
			[]string{c.topic},
			handler,
		)

		if err != nil {
			return err
		}
	}
}
