package postgres

import (
	"context"
	"database/sql"
)

type HistoryRepository struct {
	db *sql.DB
}

func NewHistoryRepository(
	db *sql.DB,
) *HistoryRepository {

	return &HistoryRepository{
		db: db,
	}
}

// TransactionCountLastHour returns the number of transactions
// made by a user in the previous one hour.
func (r *HistoryRepository) TransactionCountLastHour(
	ctx context.Context,
	userID string,
) (int, error) {

	query := `
	SELECT COUNT(*)
	FROM transactions
	WHERE user_id = $1
	  AND created_at >= NOW() - INTERVAL '1 hour';
	`

	var count int

	err := r.db.QueryRowContext(
		ctx,
		query,
		userID,
	).Scan(&count)

	if err != nil {
		return 0, err
	}

	return count, nil
}

// MerchantSeen checks whether the user has ever transacted
// with the given merchant.
func (r *HistoryRepository) MerchantSeen(
	ctx context.Context,
	userID string,
	merchant string,
) (bool, error) {

	query := `SELECT EXISTS(SELECT 1 FROM transactions WHERE user_id = $1 AND merchant = $2);`
	var exists bool
	err := r.db.QueryRowContext(ctx, query, userID, merchant).Scan(&exists)
	if err != nil {
		return false, err
	}
	return exists, nil
}

// DeviceSeen checks whether the device has been used before.
func (r *HistoryRepository) DeviceSeen(
	ctx context.Context,
	userID string,
	deviceID string,
) (bool, error) {

	query := `SELECT EXISTS(SELECT 1 FROM transactions WHERE user_id = $1 AND device_id = $2);`
	var exists bool
	err := r.db.QueryRowContext(ctx, query, userID, deviceID).Scan(&exists)
	if err != nil {
		return false, err
	}
	return exists, nil
}

// LocationSeen checks whether the user has previously
// transacted from the supplied location.
func (r *HistoryRepository) LocationSeen(
	ctx context.Context,
	userID string,
	location string,
) (bool, error) {

	query := `SELECT EXISTS(SELECT 1 FROM transactions WHERE user_id = $1 AND location = $2);`
	var exists bool
	err := r.db.QueryRowContext(ctx, query, userID, location).Scan(&exists)
	if err != nil {
		return false, err
	}
	return exists, nil
}

// MerchantFrequency returns the percentage of transactions
// performed with the supplied merchant.
func (r *HistoryRepository) MerchantFrequency(
	ctx context.Context,
	userID string,
	merchant string,
) (float64, error) {

	var merchantCount int
	err := r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM transactions WHERE user_id = $1 AND merchant = $2;`, userID, merchant).Scan(&merchantCount)
	if err != nil {
		return 0, err
	}
	var total int
	err = r.db.QueryRowContext(ctx, `SELECT COUNT(*) FROM transactions WHERE user_id = $1;`, userID).Scan(&total)
	if err != nil {
		return 0, err
	}
	if total == 0 {
		return 0, nil
	}
	return float64(merchantCount) / float64(total), nil
}

func (r *HistoryRepository) GetTransactionStats(
	ctx context.Context,
	userID string,
) (float64, float64, float64, error) {

	var avgAmount sql.NullFloat64
	var stddev sql.NullFloat64
	var avgDaily sql.NullFloat64

	// For the current phase we calculate statistics using
	// all PENDING transactions. Later, when the fraud
	// decision engine is implemented, this will be changed
	// to use SUCCESS transactions.
	err := r.db.QueryRowContext(
		ctx,
		`
		SELECT
			AVG(amount)::float8,
			COALESCE(STDDEV_POP(amount)::float8, 0)
		FROM transactions
		WHERE user_id = $1
		  AND status = 'PENDING';
		`,
		userID,
	).Scan(&avgAmount, &stddev)

	if err != nil {
		return 0, 0, 0, err
	}

	if !avgAmount.Valid {
		return 0, 0, 0, nil
	}

	err = r.db.QueryRowContext(
		ctx,
		`
		SELECT COALESCE(AVG(daily_count), 0)
		FROM (
			SELECT
				DATE(created_at) AS day,
				COUNT(*)::float8 AS daily_count
			FROM transactions
			WHERE user_id = $1
			  AND status = 'PENDING'
			GROUP BY DATE(created_at)
		) t;
		`,
		userID,
	).Scan(&avgDaily)

	if err != nil {
		return 0, 0, 0, err
	}

	return avgAmount.Float64, stddev.Float64, avgDaily.Float64, nil
}