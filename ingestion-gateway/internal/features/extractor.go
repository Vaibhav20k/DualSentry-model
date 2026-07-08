package features

import (
	"context"
	"math"
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

	baseline, _ := baselineRepo.GetBaseline(ctx, event.UserID)

	// ---------------------------------------------------------
	// Default feature values
	// ---------------------------------------------------------

	var (
		amountDeviation      float64
		amountZScore         float64
		paymentMethodChanged bool
		outsideActiveHours   bool
		outsideUsualCity     bool
	)

	// ---------------------------------------------------------
	// Baseline-derived features
	// ---------------------------------------------------------

	if baseline != nil {

		if baseline.AverageAmount != 0 {
			amountDeviation =
				(event.Amount - baseline.AverageAmount) /
					baseline.AverageAmount
		}

		if baseline.TransactionStdDev > 0 {
			amountZScore =
				(event.Amount - baseline.AverageAmount) /
					baseline.TransactionStdDev
		}

		paymentMethodChanged =
			event.PaymentMethod != baseline.PreferredPaymentMethod

		outsideUsualCity =
			event.Location != baseline.UsualCity
	}

	// ---------------------------------------------------------
	// Parse transaction timestamp
	// ---------------------------------------------------------

	parsedTime, err := time.Parse(time.RFC3339, event.Timestamp)
	if err != nil {
		parsedTime = time.Now()
	}

	hour := parsedTime.Hour()

	if baseline != nil {

		outsideActiveHours =
			hour < baseline.ActiveHourStart ||
				hour > baseline.ActiveHourEnd
	}

	// ---------------------------------------------------------
	// History-derived features
	// ---------------------------------------------------------

	txVelocity, _ :=
		historyRepo.TransactionCountLastHour(
			ctx,
			event.UserID,
		)

	merchantFrequency, _ :=
		historyRepo.MerchantFrequency(
			ctx,
			event.UserID,
			event.Merchant,
		)

	merchantSeen, _ :=
		historyRepo.MerchantSeen(
			ctx,
			event.UserID,
			event.Merchant,
		)

	deviceSeen, _ :=
		historyRepo.DeviceSeen(
			ctx,
			event.UserID,
			event.DeviceID,
		)

	locationSeen, _ :=
		historyRepo.LocationSeen(
			ctx,
			event.UserID,
			event.Location,
		)

	newMerchant := !merchantSeen
	newDevice := !deviceSeen
	newLocation := !locationSeen

	// ---------------------------------------------------------
	// Risk Flags
	// ---------------------------------------------------------

	var flags []string

	if math.Abs(amountZScore) >= 3 {
		flags = append(flags, "AMOUNT_OUTLIER")
	}

	if txVelocity > 10 {
		flags = append(flags, "HIGH_VELOCITY")
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

	if paymentMethodChanged {
		flags = append(flags, "PAYMENT_METHOD_CHANGED")
	}

	if outsideUsualCity {
		flags = append(flags, "OUTSIDE_USUAL_CITY")
	}

	if outsideActiveHours {
		flags = append(flags, "OUTSIDE_ACTIVE_HOURS")
	}

	// ---------------------------------------------------------
	// Final Feature Vector
	// ---------------------------------------------------------

	return FeatureVector{
		TransactionID: event.TransactionID,
		UserID:        event.UserID,

		TransactionType:  event.TransactionType,
		MerchantCategory: event.MerchantCategory,
		Location:         event.Location,
		DeviceID:         event.DeviceID,
		PaymentMethod:    event.PaymentMethod,

		Amount:                event.Amount,
		AmountDeviation:       amountDeviation,
		AmountZScore:          amountZScore,
		TransactionVelocity1H: txVelocity,

		HourOfDay: hour,
		DayOfWeek: int(parsedTime.Weekday()),
		IsWeekend: parsedTime.Weekday() == time.Saturday ||
			parsedTime.Weekday() == time.Sunday,

		OutsideActiveHours: outsideActiveHours,

		NewMerchant:          newMerchant,
		NewDevice:            newDevice,
		NewLocation:          newLocation,
		PaymentMethodChanged: paymentMethodChanged,
		MerchantFrequency:    merchantFrequency,

		DeviceTrustScore:         0,
		MerchantTrustScore:       0,
		LocationRiskScore:        0,
		TimeSinceLastTransaction: 0,

		RiskFlags: flags,
	}
}