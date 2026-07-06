package features

type FeatureVector struct {
	TransactionID string

	UserID string

	Amount float64

	Hour int

	IsWeekend bool

	AmountDeviation float64

	TransactionVelocity1H int

	NewMerchant bool

	NewDevice bool

	NewLocation bool

	MerchantFrequency float64

	RiskFlags []string
}