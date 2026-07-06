package repository

import "context"

type UserBaseline struct {
	UserID string

	AverageAmount float64

	TransactionStdDev float64

	AverageDailyTransactions int

	PreferredPaymentMethod string

	PreferredMerchantCategory string

	UsualCity string

	ActiveHourStart int

	ActiveHourEnd int
}

type BaselineRepository interface {

	GetBaseline(
		ctx context.Context,
		userID string,
	) (*UserBaseline, error)
}