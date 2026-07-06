package main

import (
	"log"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/postgres"
)

func main() {

	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}

	// Initialize DB connection
	db, err := postgres.NewConnection(cfg)
	if err != nil {
		log.Fatal(err)
	}

	// Create repository implementations
	baselineRepo := postgres.NewBaselineRepository(db)
	historyRepo := postgres.NewHistoryRepository(db)

	consumer, err := kafka.NewConsumer(
		cfg.KafkaBrokers,
		cfg.KafkaTopic,
		baselineRepo,
		historyRepo,
	)
	if err != nil {
		log.Fatal(err)
	}

	defer consumer.Close()

	log.Println("Starting Kafka Consumer...")

	if err := consumer.ConsumeGroup(); err != nil {
		log.Fatal(err)
	}
}