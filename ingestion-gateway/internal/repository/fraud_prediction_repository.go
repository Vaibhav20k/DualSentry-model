package repository

import "context"

type FraudPrediction struct {
	TransactionID    string   `json:"transactionID"`
	UserID           string   `json:"userID"`
	FraudProbability float64  `json:"fraudProbability"`
	Confidence       float64  `json:"confidence"`
	Prediction       bool     `json:"prediction"`
	Decision         string   `json:"decision"`
	Threshold        float64  `json:"threshold"`
	ModelVersion     string   `json:"modelVersion"`
	RiskFlags        []string `json:"riskFlags"`
}

type DashboardSummary struct {
	TotalTransactions int     `json:"totalTransactions"`
	Fraudulent        int     `json:"fraudulent"`
	Review            int     `json:"review"`
	Allowed           int     `json:"allowed"`
	FraudRate         float64 `json:"fraudRate"`
}

type FraudTrendPoint struct {
	Time  string `json:"time"`
	Count int    `json:"count"`
}

type FraudPredictionRepository interface {
	SavePrediction(
		ctx context.Context,
		prediction FraudPrediction,
	) error

	GetAllPredictions(
		ctx context.Context,
	) ([]FraudPrediction, error)

	GetDashboardSummary(
		ctx context.Context,
	) (DashboardSummary, error)

	GetPredictionByTransactionID(
		ctx context.Context,
		transactionID string,
	) (FraudPrediction, error)

	GetFraudTrend(
		ctx context.Context,
	) ([]FraudTrendPoint, error)
}
