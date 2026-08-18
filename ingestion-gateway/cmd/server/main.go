package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/handler/logger"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/metrics"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/server"
)

func main() {

	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("configuration error: %v", err)
	}

	// Initialize Prometheus metrics
	metrics.Init()

	// Initialize logger
	appLogger := logger.New()

	appLogger.Println("Configuration loaded successfully")

	// Create servers
	grpcServer := server.New(cfg)
	httpServer := server.NewHTTPServer(cfg)

	// Start HTTP server
	go func() {

		appLogger.Printf(
			"Starting HTTP server on port %s",
			cfg.HTTPPort,
		)

		if err := httpServer.Start(); err != nil &&
			err != http.ErrServerClosed {

			appLogger.Fatalf(
				"HTTP Server failed: %v",
				err,
			)
		}
	}()

	// Start gRPC server
	go func() {

		appLogger.Printf(
			"Starting gRPC server on port %s",
			cfg.ServerPort,
		)

		if err := grpcServer.Start(); err != nil {

			appLogger.Fatalf(
				"gRPC Server failed: %v",
				err,
			)
		}
	}()

	// Wait for shutdown signal
	stop := make(chan os.Signal, 1)

	signal.Notify(
		stop,
		os.Interrupt,
		syscall.SIGTERM,
	)

	<-stop

	appLogger.Println("Shutdown signal received...")

	ctx, cancel := context.WithTimeout(
		context.Background(),
		15*time.Second,
	)
	defer cancel()

	if err := httpServer.Stop(ctx); err != nil {

		appLogger.Printf(
			"HTTP shutdown error: %v",
			err,
		)
	}

	appLogger.Println("Stopping gRPC server...")
	grpcServer.Stop()

	appLogger.Println("Application stopped gracefully.")
}
