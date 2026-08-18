package repository

import (
	"database/sql"
)

type AlertRepository struct {
	db *sql.DB
}

func NewAlertRepository(db *sql.DB) *AlertRepository {
	return &AlertRepository{
		db: db,
	}
}

func (r *AlertRepository) CreateManualReview(
	transactionID string,
	fraudProbability float64,
) error {

	_, err := r.db.Exec(`
		INSERT INTO manual_review_queue
		(transaction_id, fraud_probability)
		VALUES ($1, $2)
	`,
		transactionID,
		fraudProbability,
	)

	return err
}

func (r *AlertRepository) CreateFraudAlert(
	transactionID string,
	fraudProbability float64,
	alertType string,
) error {

	_, err := r.db.Exec(`
		INSERT INTO fraud_alerts
		(transaction_id, fraud_probability, alert_type)
		VALUES ($1, $2, $3)
	`,
		transactionID,
		fraudProbability,
		alertType,
	)

	return err
}
