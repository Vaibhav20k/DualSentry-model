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

	var paymentMethod sql.NullString
	var merchantCategory sql.NullString
	var city sql.NullString
	var activeStart sql.NullInt16
	var activeEnd sql.NullInt16

	err := r.db.QueryRowContext(
		ctx,
		query,
		userID,
	).Scan(
		&baseline.UserID,
		&baseline.AverageAmount,
		&baseline.TransactionStdDev,
		&baseline.AverageDailyTransactions,
		&paymentMethod,
		&merchantCategory,
		&city,
		&activeStart,
		&activeEnd,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}

	if paymentMethod.Valid {
		baseline.PreferredPaymentMethod = paymentMethod.String
	}

	if merchantCategory.Valid {
		baseline.PreferredMerchantCategory = merchantCategory.String
	}

	if city.Valid {
		baseline.UsualCity = city.String
	}

	if activeStart.Valid {
		baseline.ActiveHourStart = int(activeStart.Int16)
	}

	if activeEnd.Valid {
		baseline.ActiveHourEnd = int(activeEnd.Int16)
	}

	return &baseline, nil
}

func (r *BaselineRepository) UpsertBaseline(
	ctx context.Context,
	baseline *repository.UserBaseline,
) error {

	query := `
	INSERT INTO user_baselines (
		user_id,
		average_transaction_amount,
		transaction_amount_stddev,
		average_daily_transactions,
		preferred_payment_method,
		preferred_merchant_category,
		usual_city,
		active_hours_start,
		active_hours_end,
		last_updated
	)
	VALUES (
		$1,
		$2,
		$3,
		$4,
		NULL,
		NULL,
		NULL,
		NULL,
		NULL,
		NOW()
	)
	ON CONFLICT (user_id)
	DO UPDATE SET
		average_transaction_amount = EXCLUDED.average_transaction_amount,
		transaction_amount_stddev = EXCLUDED.transaction_amount_stddev,
		average_daily_transactions = EXCLUDED.average_daily_transactions,
		last_updated = NOW();
	`

	_, err := r.db.ExecContext(
		ctx,
		query,
		baseline.UserID,
		baseline.AverageAmount,
		baseline.TransactionStdDev,
		baseline.AverageDailyTransactions,
	)

	return err
}