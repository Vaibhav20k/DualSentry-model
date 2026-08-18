package generator

import (
	"math/rand"

	"github.com/Vaibhav20k/fintech-pipeline/transaction-simulator/internal/models"
)

const FraudProbability = 0.05

func InjectFraud(tx *models.Transaction) {

	if rand.Float64() > FraudProbability {
		return
	}

	switch rand.Intn(4) {

	case 0:
		// High Amount
		tx.Amount *= 20

	case 1:
		// New Device
		tx.DeviceID = "fraud_device_001"

	case 2:
		// New Location
		tx.Location = "Dubai"

	case 3:
		// High Amount + New Device
		tx.Amount *= 15
		tx.DeviceID = "fraud_device_002"
	}
}
