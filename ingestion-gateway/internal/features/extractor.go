package features

import (
	"context"
	"time"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

func BuildFeatureVector(
	event events.TransactionEvent,
	baselineRepo repository.BaselineRepository,
	historyRepo repository.HistoryRepository,
) FeatureVector {

	ctx := context.Background()

	// Fetch baseline if available
	baseline, _ := baselineRepo.GetBaseline(ctx, event.UserID)

	// Compute amount deviation
	var amountDev float64
	if baseline != nil && baseline.AverageAmount != 0 {
		amountDev = (event.Amount - baseline.AverageAmount) / baseline.AverageAmount
	}

	// History stats
	txCount, _ := historyRepo.TransactionCountLastHour(ctx, event.UserID)
	merchantFreq, _ := historyRepo.MerchantFrequency(ctx, event.UserID, event.Merchant)
	merchantSeen, _ := historyRepo.MerchantSeen(ctx, event.UserID, event.Merchant)
	deviceSeen, _ := historyRepo.DeviceSeen(ctx, event.UserID, event.DeviceID)
	locationSeen, _ := historyRepo.LocationSeen(ctx, event.UserID, event.Location)

	newMerchant := !merchantSeen
	newDevice := !deviceSeen
	newLocation := !locationSeen

	now := time.Now()

	// Risk flags based on simple deterministic rules
	var flags []string
	if amountDev > 1.0 {
		flags = append(flags, "HIGH_AMOUNT")
	}
	if newMerchant {
		flags = append(flags, "NEW_MERCHANT")
	}
	if newDevice {
		flags = append(flags, "NEW_DEVICE")
	}
	if newLocation {
		flags = append(flags, "NEW_LOCATION")
	}
	if txCount > 10 { // arbitrary high velocity threshold
		flags = append(flags, "HIGH_TRANSACTION_VELOCITY")
	}

	return FeatureVector{
		TransactionID:      event.TransactionID,
		UserID:             event.UserID,
		Amount:             event.Amount,
		Hour:               now.Hour(),
		IsWeekend:          now.Weekday() == time.Saturday || now.Weekday() == time.Sunday,
		AmountDeviation:    amountDev,
		TransactionVelocity1H: txCount,
		NewMerchant:        newMerchant,
		NewDevice:          newDevice,
		NewLocation:        newLocation,
		MerchantFrequency:  merchantFreq,
		RiskFlags:          flags,
	}
}