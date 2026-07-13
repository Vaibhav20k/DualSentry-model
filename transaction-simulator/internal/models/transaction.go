package models

type Transaction struct {
	UserID            string  `json:"user_id"`
	Timestamp         string  `json:"timestamp"`

	Amount            float64 `json:"amount"`
	Currency          string  `json:"currency"`
	TransactionType   string  `json:"transaction_type"`

	PaymentMethod     string  `json:"payment_method"`
	PaymentIdentifier string  `json:"payment_identifier"`

	Merchant          string  `json:"merchant"`
	MerchantCategory  string  `json:"merchant_category"`
	ReceiverAccount   string  `json:"receiver_account"`

	Location          string  `json:"location"`
	IPAddress         string  `json:"ip_address"`
	DeviceID          string  `json:"device_id"`
}