package models

type UserProfile struct {
	ID string

	HomeCity string

	PreferredPayment string

	FavoriteMerchant string

	AverageAmount float64

	DeviceID string

	IPAddress string

	ActiveStartHour int
	ActiveEndHour   int
}
