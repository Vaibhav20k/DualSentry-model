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

	avgAmount, stdDev, avgDailyTx, err := u.HistoryRepo.GetTransactionStats(ctx, userID)
	if err != nil {
		log.Printf("[BaselineUpdater] failed to get transaction stats: %v", err)
		return err
	}

	log.Printf(
		"[BaselineUpdater] Stats -> avg=%.2f stddev=%.2f avgDaily=%.2f",
		avgAmount,
		stdDev,
		avgDailyTx,
	)

	baseline := &repository.UserBaseline{
		UserID:                   userID,
		AverageAmount:            avgAmount,
		TransactionStdDev:        stdDev,
		AverageDailyTransactions: int(avgDailyTx),
	}

	if err = u.BaselineRepo.UpsertBaseline(ctx, baseline); err != nil {
		log.Printf("[BaselineUpdater] failed to upsert baseline: %v", err)
		return err
	}

	log.Printf("[BaselineUpdater] Baseline successfully updated")

	return nil
}