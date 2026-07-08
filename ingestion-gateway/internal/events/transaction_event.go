package events

type TransactionEvent struct {

	// ==========================================================
	// Transaction Metadata
	// ==========================================================

	TransactionID string `json:"transaction_id"`
	UserID        string `json:"user_id"`

	Timestamp string `json:"timestamp"`

	// ==========================================================
	// Transaction Details
	// ==========================================================

	Amount float64 `json:"amount"`

	Currency string `json:"currency"`

	TransactionType string `json:"transaction_type"`

	PaymentMethod string `json:"payment_method"`

	PaymentIdentifier string `json:"payment_identifier"`

	Merchant string `json:"merchant"`

	MerchantCategory string `json:"merchant_category"`

	ReceiverAccount string `json:"receiver_account"`

	// ==========================================================
	// Device / Network
	// ==========================================================

	Location string `json:"location"`

	IPAddress string `json:"ip_address"`

	DeviceID string `json:"device_id"`

	// ==========================================================
	// Status
	// ==========================================================

	Status string `json:"status"`
}