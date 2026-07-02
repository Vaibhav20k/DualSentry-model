package main

import (
	"log"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/logger"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/server"
)

func main() {

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("configuration error: %v", err)
	}

	// Initialize logger
	appLogger := logger.New()

	appLogger.Println("Configuration loaded successfully")

	// Create gRPC server
	grpcServer := server.New(cfg.ServerPort)

	appLogger.Printf("Starting gRPC server on port %s", cfg.ServerPort)

	// Start server
	if err := grpcServer.Start(); err != nil {
		appLogger.Fatalf("Server failed: %v", err)
	}
}
