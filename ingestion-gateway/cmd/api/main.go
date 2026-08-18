package main

import (
	"log"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/config"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/server"
)

func main() {

	cfg, err := config.Load()
	if err != nil {
		log.Fatal(err)
	}

	apiServer := server.NewHTTPServer(cfg)

	log.Println("Starting REST API Server...")

	if err := apiServer.Start(); err != nil {
		log.Fatal(err)
	}
}
