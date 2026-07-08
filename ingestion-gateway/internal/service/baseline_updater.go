package service

import (
	"context"
	"log"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

// BaselineUpdater orchestrates the calculation and persistence of a user's baseline.
type BaselineUpdater struct {
	HistoryRepo  repository.HistoryRepository
	BaselineRepo repository.BaselineRepository
}

// NewBaselineUpdater constructs a BaselineUpdater.
func NewBaselineUpdater(
	historyRepo repository.HistoryRepository,
	baselineRepo repository.BaselineRepository,
) *BaselineUpdater {

	return &BaselineUpdater{
		HistoryRepo:  historyRepo,
		BaselineRepo: baselineRepo,
	}
}

// UpdateBaseline recalculates the baseline for the given user.
func (u *BaselineUpdater) UpdateBaseline(
	ctx context.Context,
	userID string,
) error {

	log.Printf("[BaselineUpdater] Updating baseline for user: %s", userID)

	// Transaction statistics
	avgAmount, stdDev, avgDailyTx, err := u.HistoryRepo.GetTransactionStats(ctx, userID)
	if err != nil {
		log.Printf("[BaselineUpdater] failed to get transaction stats: %v", err)
		return err
	}

	// Preferred payment method
	paymentMethod, err := u.HistoryRepo.PreferredPaymentMethod(ctx, userID)
	if err != nil {
		log.Printf("[BaselineUpdater] failed to get preferred payment method: %v", err)
		return err
	}

	// Preferred merchant category
	merchantCategory, err := u.HistoryRepo.PreferredMerchantCategory(ctx, userID)
	if err != nil {
		log.Printf("[BaselineUpdater] failed to get preferred merchant category: %v", err)
		return err
	}

	// Usual city
	city, err := u.HistoryRepo.UsualCity(ctx, userID)
	if err != nil {
		log.Printf("[BaselineUpdater] failed to get usual city: %v", err)
		return err
	}

	// Active hours
	startHour, endHour, err := u.HistoryRepo.ActiveHours(ctx, userID)
	if err != nil {
		log.Printf("[BaselineUpdater] failed to get active hours: %v", err)
		return err
	}

	// ===============================
	// DEBUG OUTPUT
	// ===============================
	log.Println("========================================")
	log.Println(" BASELINE DEBUG")
	log.Println("========================================")
	log.Printf("User ID                  : %s", userID)
	log.Printf("Average Amount           : %.2f", avgAmount)
	log.Printf("Transaction StdDev       : %.2f", stdDev)
	log.Printf("Average Daily Tx         : %.2f", avgDailyTx)
	log.Printf("Preferred Payment Method : %q", paymentMethod)
	log.Printf("Preferred Merchant Cat   : %q", merchantCategory)
	log.Printf("Usual City               : %q", city)
	log.Printf("Active Hours             : %d - %d", startHour, endHour)
	log.Println("========================================")

	baseline := &repository.UserBaseline{
		UserID:                    userID,
		AverageAmount:             avgAmount,
		TransactionStdDev:         stdDev,
		AverageDailyTransactions:  int(avgDailyTx),
		PreferredPaymentMethod:    paymentMethod,
		PreferredMerchantCategory: merchantCategory,
		UsualCity:                 city,
		ActiveHourStart:           startHour,
		ActiveHourEnd:             endHour,
	}

	if err := u.BaselineRepo.UpsertBaseline(ctx, baseline); err != nil {
		log.Printf("[BaselineUpdater] failed to upsert baseline: %v", err)
		return err
	}

	log.Printf("[BaselineUpdater] Baseline successfully updated")

	return nil
}