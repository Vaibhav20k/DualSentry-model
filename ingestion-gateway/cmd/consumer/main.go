package main

import (
	"log"
	"net/http"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/decision"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/ml"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/postgres"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {

	cfg, err := config.Load()

	if err != nil {
		log.Fatal(err)
	}
	metrics.Init()

	// -----------------------------
	// Database
	// -----------------------------
	db, err := postgres.NewConnection(cfg)
	if err != nil {
		log.Fatal(err)
	}

	// -----------------------------
	// Repositories
	// -----------------------------
	baselineRepo := postgres.NewBaselineRepository(db)
	historyRepo := postgres.NewHistoryRepository(db)
	predictionRepo := postgres.NewFraudPredictionRepository(db)
	alertRepo := repository.NewAlertRepository(db)

	// -----------------------------
	// ML Client
	// -----------------------------
	mlClient := ml.NewClient("")

	// -----------------------------
	// Decision Engine
	// -----------------------------
	engine := decision.NewEngine()

	// -----------------------------
	// Retry Producer
	// -----------------------------
	retryProducer, err := kafka.NewProducer(
		cfg.KafkaBrokers,
		"transactions.retry",
	)
	if err != nil {
		log.Fatal(err)
	}
	defer retryProducer.Close()

	// -----------------------------
	// DLQ Producer
	// -----------------------------
	dlqProducer, err := kafka.NewProducer(
		cfg.KafkaBrokers,
		"transactions.dlq",
	)
	if err != nil {
		log.Fatal(err)
	}
	defer dlqProducer.Close()

	// -----------------------------
	// Kafka Consumer
	// -----------------------------
	consumer, err := kafka.NewConsumer(
		cfg.KafkaBrokers,
		cfg.KafkaTopic,

		baselineRepo,
		historyRepo,
		predictionRepo,

		mlClient,
		engine,
		alertRepo,

		retryProducer,
		dlqProducer,
	)
	if err != nil {
		log.Fatal(err)
	}

	defer consumer.Close()

	log.Println("Starting Kafka Consumers...")

	go func() {
		http.Handle("/metrics", promhttp.Handler())

		log.Println("Consumer metrics exposed on :9091/metrics")

		if err := http.ListenAndServe(":9091", nil); err != nil {
			log.Fatal(err)
		}
	}()

	// Start RAW consumer
	go func() {
		if err := consumer.Consume(); err != nil {
			log.Fatal(err)
		}
	}()

	// Start RETRY consumer
	go func() {
		if err := consumer.ConsumeRetry(); err != nil {
			log.Fatal(err)
		}
	}()

	// Keep the application alive
	select {}
}
