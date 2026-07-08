package repository

import "context"

type HistoryRepository interface {

	// TransactionCountLastHour returns the number of transactions
	// made by the user during the last hour.
	TransactionCountLastHour(
		ctx context.Context,
		userID string,
	) (int, error)

	// GetTransactionStats returns:
	// - average transaction amount
	// - transaction amount standard deviation
	// - average daily transaction count
	GetTransactionStats(
		ctx context.Context,
		userID string,
	) (float64, float64, float64, error)

	// MerchantSeen checks whether the user has
	// transacted with this merchant before.
	MerchantSeen(
		ctx context.Context,
		userID string,
		merchant string,
	) (bool, error)

	// DeviceSeen checks whether the device
	// has been used previously by the user.
	DeviceSeen(
		ctx context.Context,
		userID string,
		deviceID string,
	) (bool, error)

	// LocationSeen checks whether the user has
	// previously transacted from this location.
	LocationSeen(
		ctx context.Context,
		userID string,
		location string,
	) (bool, error)

	// MerchantFrequency returns the fraction of
	// transactions made with the supplied merchant.
	MerchantFrequency(
		ctx context.Context,
		userID string,
		merchant string,
	) (float64, error)

	// PreferredPaymentMethod returns the user's
	// most frequently used payment method.
	PreferredPaymentMethod(
		ctx context.Context,
		userID string,
	) (string, error)

	// PreferredMerchantCategory returns the user's
	// most frequently used merchant category.
	PreferredMerchantCategory(
		ctx context.Context,
		userID string,
	) (string, error)

	// UsualCity returns the city from which the
	// user most frequently transacts.
	UsualCity(
		ctx context.Context,
		userID string,
	) (string, error)

	// ActiveHours returns the user's most active
	// transaction window (start hour, end hour).
	ActiveHours(
		ctx context.Context,
		userID string,
	) (int, int, error)
}