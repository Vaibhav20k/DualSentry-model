package postgres

import (
	"context"
	"database/sql"
)

type AnomalyRepository struct {
	db *sql.DB
}

func NewAnomalyRepository(
	db *sql.DB,
) *AnomalyRepository {

	return &AnomalyRepository{
		db: db,
	}
}

func (r *AnomalyRepository) SavePrediction(
	ctx context.Context,
	transactionID string,
	anomalyScore float64,
	anomalyType string,
	modelName string,
	modelVersion string,
	explanation string,
) error {

	query := `
	INSERT INTO anomaly_logs (
		transaction_id,
		anomaly_score,
		anomaly_type,
		model_name,
		model_version,
		explanation
	)
	VALUES (
		$1,$2,$3,$4,$5,$6
	);
	`

	_, err := r.db.ExecContext(
		ctx,
		query,
		transactionID,
		anomalyScore,
		anomalyType,
		modelName,
		modelVersion,
		explanation,
	)

	return err
}
