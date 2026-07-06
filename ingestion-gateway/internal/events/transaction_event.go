package events

type TransactionEvent struct {
	TransactionID     string  `json:"transaction_id"`
	UserID            string  `json:"user_id"`
	Amount            float64 `json:"amount"`
	Currency          string  `json:"currency"`
	PaymentMethod     string  `json:"payment_method"`
	PaymentIdentifier string  `json:"payment_identifier"`
	Merchant          string  `json:"merchant"`
	ReceiverAccount   string  `json:"receiver_account"`
	Location          string  `json:"location"`
	IPAddress         string  `json:"ip_address"`
	DeviceID          string  `json:"device_id"`
	Status            string  `json:"status"`
}