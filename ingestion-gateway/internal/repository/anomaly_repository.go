package repository

import "context"

type AnomalyRepository interface {
	SavePrediction(
		ctx context.Context,
		transactionID string,
		anomalyScore float64,
		anomalyType string,
		modelName string,
		modelVersion string,
		explanation string,
	) error
}
