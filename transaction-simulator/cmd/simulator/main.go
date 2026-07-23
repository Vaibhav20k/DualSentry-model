package main

import (
	"log"
	"math/rand"
	"time"

	"github.com/Vaibhav20k/fintech-pipeline/transaction-simulator/internal/client"
	"github.com/Vaibhav20k/fintech-pipeline/transaction-simulator/internal/generator"
)

func main() {

	rand.Seed(time.Now().UnixNano())
	generator.InitUsers(1000)

	api := client.New("http://ingestion-gateway:8080")

	log.Println("======================================")
	log.Println(" FinTech Transaction Simulator Started")
	log.Println("======================================")

	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for range ticker.C {

		tx := generator.Generate()

		err := api.SendTransaction(tx)

		if err != nil {

			log.Printf(
				"FAILED -> %v",
				err,
			)

			continue
		}

		log.Printf(
			"Transaction Sent | %s | ₹%.2f | %s",
			tx.Merchant,
			tx.Amount,
			tx.Location,
		)
	}
}