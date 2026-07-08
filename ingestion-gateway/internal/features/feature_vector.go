package features

// FeatureVector represents the engineered features extracted from a
// transaction before being sent to the anomaly detection engine.
//
// This struct intentionally contains only ML features.
// It should NOT contain business/domain objects.
type FeatureVector struct {

	// ==========================================================
	// Transaction Metadata
	// ==========================================================

	TransactionID string
	UserID        string

	// ==========================================================
	// Categorical Features
	// ==========================================================

	TransactionType string

	MerchantCategory string

	Location string

	DeviceID string

	PaymentMethod string

	// ==========================================================
	// Numerical Features
	// ==========================================================

	Amount float64

	// Difference between current amount and user's historical average.
	AmountDeviation float64

	// Standardized anomaly score.
	// (Amount - Mean) / StdDev
	AmountZScore float64

	// Number of transactions in the last hour.
	TransactionVelocity1H int

	// ==========================================================
	// Temporal Features
	// ==========================================================

	HourOfDay int

	DayOfWeek int

	IsWeekend bool

	OutsideActiveHours bool

	// ==========================================================
	// Behaviour Features
	// ==========================================================

	NewMerchant bool

	NewDevice bool

	NewLocation bool

	PaymentMethodChanged bool

	MerchantFrequency float64

	// ==========================================================
	// Future Features
	// ==========================================================

	DeviceTrustScore float64

	MerchantTrustScore float64

	LocationRiskScore float64

	TimeSinceLastTransaction float64

	// ==========================================================
	// Labels
	// ==========================================================

	RiskFlags []string
}