package ml

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"math"
	"net/http"
	"time"
	"os"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/features"
)

const (
	DefaultMLServiceURL = "http://ml-anomaly-engine:8000"
)

type Client struct {
	baseURL    string
	httpClient *http.Client
}

func NewClient(baseURL string) *Client {
	if baseURL == "" {
		baseURL = os.Getenv("ML_SERVICE_URL")
	}
	if baseURL == "" {
		baseURL = DefaultMLServiceURL
	}
	if baseURL == "" {
		baseURL = "http://ml-anomaly-engine:8000"
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
	Confidence       float64 `json:"confidence"`
}

func (c *Client) Predict(
	ctx context.Context,
	vector features.FeatureVector,
) (*PredictionResponse, error) {

	payload := map[string]any{
		"amount": vector.Amount,

		"payment_channel": vector.PaymentMethod,

		"time_since_last_transaction": vector.TimeSinceLastTransaction,

		"velocity_score": vector.TransactionVelocity1H,

		// Clamp to non-negative: ML model schema requires Field(ge=0)
		"spending_deviation_score": math.Max(0, vector.AmountDeviation),

		"is_first_transaction": 0,

		"hour": vector.HourOfDay,

		"day_of_week": vector.DayOfWeek,

		"month": int(time.Now().Month()),

		"is_weekend": boolToInt(vector.IsWeekend),

		"is_cross_bank_transfer": 0,

		"is_cross_currency_transfer": 0,

		"is_new_receiver": boolToInt(vector.NewMerchant),

		"is_new_bank": 0,

		"is_new_payment_format": boolToInt(vector.PaymentMethodChanged),
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
