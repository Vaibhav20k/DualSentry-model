package ml

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/features"
)

const (
	DefaultMLServiceURL = "http://localhost:8000"
)

type Client struct {
	baseURL    string
	httpClient *http.Client
}

func NewClient(
	baseURL string,
) *Client {

	if baseURL == "" {
		baseURL = DefaultMLServiceURL
	}

	return &Client{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

type PredictionResponse struct {
	FraudProbability float64 `json:"fraud_probability"`
	Prediction       bool    `json:"prediction"`
	Threshold        float64 `json:"threshold"`
	ModelVersion     string  `json:"model_version"`
}

func (c *Client) Predict(
	ctx context.Context,
	vector features.FeatureVector,
) (*PredictionResponse, error) {

	payload := map[string]any{
		"amount": vector.Amount,

		"transaction_type": vector.TransactionType,

		"merchant_category": vector.MerchantCategory,

		"location": vector.Location,

		"device_used": vector.DeviceID,

		"payment_channel": vector.PaymentMethod,

		"time_since_last_transaction": vector.TimeSinceLastTransaction,

		"spending_deviation_score": vector.AmountDeviation,

		"velocity_score": vector.TransactionVelocity1H,

		"geo_anomaly_score": vector.LocationRiskScore,

		"hour": vector.HourOfDay,

		"day_of_week": vector.DayOfWeek,

		"month": 1,

		"is_weekend": boolToInt(vector.IsWeekend),

		"is_first_transaction": 0,
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		c.baseURL+"/predict",
		bytes.NewBuffer(body),
	)
	if err != nil {
		return nil, err
	}

	req.Header.Set(
		"Content-Type",
		"application/json",
	)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf(
			"ml service returned %d",
			resp.StatusCode,
		)
	}

	var prediction PredictionResponse

	err = json.NewDecoder(
		resp.Body,
	).Decode(&prediction)
	if err != nil {
		return nil, err
	}

	return &prediction, nil
}

func boolToInt(
	value bool,
) int {

	if value {
		return 1
	}

	return 0
}