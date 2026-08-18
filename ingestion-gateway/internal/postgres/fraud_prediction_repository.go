package postgres

import (
	"context"
	"database/sql"
	"encoding/json"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

type FraudPredictionRepository struct {
	db *sql.DB
}

func NewFraudPredictionRepository(
	db *sql.DB,
) *FraudPredictionRepository {

	return &FraudPredictionRepository{
		db: db,
	}
}

func (r *FraudPredictionRepository) SavePrediction(
	ctx context.Context,
	prediction repository.FraudPrediction,
) error {

	riskFlagsJSON, err := json.Marshal(
		prediction.RiskFlags,
	)
	if err != nil {
		return err
	}

	_, err = r.db.ExecContext(
		ctx,
		`
		INSERT INTO fraud_predictions
		(
			transaction_id,
			user_id,
			fraud_probability,
			confidence,
			prediction,
			decision,
			threshold,
			model_version,
			risk_flags
		)
		VALUES
		(
			$1,$2,$3,$4,$5,$6,$7,$8,$9
		)
		`,
		prediction.TransactionID,
		prediction.UserID,
		prediction.FraudProbability,
		prediction.Confidence,
		prediction.Prediction,
		prediction.Decision,
		prediction.Threshold,
		prediction.ModelVersion,
		riskFlagsJSON,
	)

	return err
}

func (r *FraudPredictionRepository) GetAllPredictions(
	ctx context.Context,
) ([]repository.FraudPrediction, error) {

	rows, err := r.db.QueryContext(
		ctx,
		`
		SELECT
			transaction_id,
			user_id,
			fraud_probability,
			confidence,
			prediction,
			decision,
			threshold,
			model_version,
			risk_flags
		FROM fraud_predictions
		ORDER BY created_at DESC
		`,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var predictions []repository.FraudPrediction

	for rows.Next() {

		var (
			p             repository.FraudPrediction
			riskFlagsJSON []byte
		)

		err := rows.Scan(
			&p.TransactionID,
			&p.UserID,
			&p.FraudProbability,
			&p.Confidence,
			&p.Prediction,
			&p.Decision,
			&p.Threshold,
			&p.ModelVersion,
			&riskFlagsJSON,
		)
		if err != nil {
			return nil, err
		}

		if len(riskFlagsJSON) > 0 {
			if err := json.Unmarshal(
				riskFlagsJSON,
				&p.RiskFlags,
			); err != nil {
				return nil, err
			}
		}

		predictions = append(
			predictions,
			p,
		)
	}

	return predictions, rows.Err()
}

func (r *FraudPredictionRepository) GetDashboardSummary(
	ctx context.Context,
) (repository.DashboardSummary, error) {

	var summary repository.DashboardSummary

	err := r.db.QueryRowContext(
		ctx,
		`
		SELECT
			COUNT(*) AS total_transactions,

			COUNT(*) FILTER (
				WHERE prediction = true
			) AS fraudulent,

			COUNT(*) FILTER (
				WHERE decision = 'REVIEW'
			) AS review,

			COUNT(*) FILTER (
				WHERE decision = 'ALLOW'
			) AS allowed,

			COALESCE(
				ROUND(
					(
						COUNT(*) FILTER (
							WHERE prediction = true
						)::numeric * 100
					)
					/
					NULLIF(COUNT(*),0),
					2
				),
				0
			) AS fraud_rate

		FROM fraud_predictions
		`,
	).Scan(
		&summary.TotalTransactions,
		&summary.Fraudulent,
		&summary.Review,
		&summary.Allowed,
		&summary.FraudRate,
	)

	return summary, err
}

func (r *FraudPredictionRepository) GetPredictionByTransactionID(
	ctx context.Context,
	transactionID string,
) (repository.FraudPrediction, error) {

	var prediction repository.FraudPrediction

	err := r.db.QueryRowContext(
		ctx,
		`
		SELECT
			transaction_id,
			user_id,
			fraud_probability,
			prediction,
			decision,
			threshold,
			model_version,
			risk_flags
		FROM fraud_predictions
		WHERE transaction_id = $1
		`,
		transactionID,
	).Scan(
		&prediction.TransactionID,
		&prediction.UserID,
		&prediction.FraudProbability,
		&prediction.Prediction,
		&prediction.Decision,
		&prediction.Threshold,
		&prediction.ModelVersion,
		&prediction.RiskFlags,
		&prediction.Confidence,
	)

	return prediction, err
}

func (r *FraudPredictionRepository) GetFraudTrend(
	ctx context.Context,
) ([]repository.FraudTrendPoint, error) {

	rows, err := r.db.QueryContext(
		ctx,
		`
		SELECT
			TO_CHAR(
				DATE_TRUNC('hour', created_at),
				'HH24:00'
			) AS hour,

			COUNT(*)

		FROM fraud_predictions

		GROUP BY DATE_TRUNC('hour', created_at)

		ORDER BY DATE_TRUNC('hour', created_at)
		`,
	)

	if err != nil {
		return nil, err
	}

	defer rows.Close()

	var trend []repository.FraudTrendPoint

	for rows.Next() {

		var point repository.FraudTrendPoint

		if err := rows.Scan(
			&point.Time,
			&point.Count,
		); err != nil {
			return nil, err
		}

		trend = append(trend, point)
	}

	return trend, rows.Err()
}
