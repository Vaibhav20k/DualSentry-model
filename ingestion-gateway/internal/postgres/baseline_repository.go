package postgres

import (
	"context"
	"database/sql"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

type BaselineRepository struct {
	db *sql.DB
}

func NewBaselineRepository(
	db *sql.DB,
) *BaselineRepository {

	return &BaselineRepository{
		db: db,
	}
}

func (r *BaselineRepository) GetBaseline(
	ctx context.Context,
	userID string,
) (*repository.UserBaseline, error) {

	query := `
	SELECT
		user_id,
		average_transaction_amount,
		transaction_amount_stddev,
		average_daily_transactions,
		preferred_payment_method,
		preferred_merchant_category,
		usual_city,
		active_hours_start,
		active_hours_end
	FROM user_baselines
	WHERE user_id = $1;
	`

	var baseline repository.UserBaseline

	err := r.db.QueryRowContext(
		ctx,
		query,
		userID,
	).Scan(
		&baseline.UserID,
		&baseline.AverageAmount,
		&baseline.TransactionStdDev,
		&baseline.AverageDailyTransactions,
		&baseline.PreferredPaymentMethod,
		&baseline.PreferredMerchantCategory,
		&baseline.UsualCity,
		&baseline.ActiveHourStart,
		&baseline.ActiveHourEnd,
	)

	if err != nil {

		if err == sql.ErrNoRows {
			return nil, nil
		}

		return nil, err
	}

	return &baseline, nil
}