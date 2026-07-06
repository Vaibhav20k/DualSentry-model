package repository

import "context"

type HistoryRepository interface {

	TransactionCountLastHour(
		ctx context.Context,
		userID string,
	) (int, error)

	MerchantSeen(
		ctx context.Context,
		userID string,
		merchant string,
	) (bool, error)

	DeviceSeen(
		ctx context.Context,
		userID string,
		deviceID string,
	) (bool, error)

	LocationSeen(
		ctx context.Context,
		userID string,
		location string,
	) (bool, error)

	MerchantFrequency(
		ctx context.Context,
		userID string,
		merchant string,
	) (float64, error)
}