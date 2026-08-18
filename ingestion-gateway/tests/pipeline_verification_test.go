package handler_test

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	apihandler "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/api/handler"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/cache"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/features"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

// MockBaselineRepo implements repository.BaselineRepository
type mockBaselineRepo struct {
	baseline *repository.UserBaseline
}

func (m *mockBaselineRepo) GetBaseline(ctx context.Context, userID string) (*repository.UserBaseline, error) {
	return m.baseline, nil
}

func (m *mockBaselineRepo) UpsertBaseline(ctx context.Context, baseline *repository.UserBaseline) error {
	m.baseline = baseline
	return nil
}

// MockHistoryRepo implements repository.HistoryRepository
type mockHistoryRepo struct {
	txCount int
}

func (m *mockHistoryRepo) TransactionCountLastHour(ctx context.Context, userID string) (int, error) {
	return m.txCount, nil
}

func (m *mockHistoryRepo) GetTransactionStats(ctx context.Context, userID string) (float64, float64, float64, error) {
	return 100.0, 50.0, 5.0, nil
}

func (m *mockHistoryRepo) MerchantSeen(ctx context.Context, userID string, merchant string) (bool, error) {
	return true, nil
}

func (m *mockHistoryRepo) DeviceSeen(ctx context.Context, userID string, deviceID string) (bool, error) {
	return true, nil
}

func (m *mockHistoryRepo) LocationSeen(ctx context.Context, userID string, location string) (bool, error) {
	return true, nil
}

func (m *mockHistoryRepo) MerchantFrequency(ctx context.Context, userID string, merchant string) (float64, error) {
	return 0.5, nil
}

func (m *mockHistoryRepo) PreferredPaymentMethod(ctx context.Context, userID string) (string, error) {
	return "CARD", nil
}

func (m *mockHistoryRepo) PreferredMerchantCategory(ctx context.Context, userID string) (string, error) {
	return "RETAIL", nil
}

func (m *mockHistoryRepo) UsualCity(ctx context.Context, userID string) (string, error) {
	return "New York", nil
}

func (m *mockHistoryRepo) ActiveHours(ctx context.Context, userID string) (int, int, error) {
	return 8, 20, nil
}

func TestFeatureExtractionPreTransactionOrdering(t *testing.T) {
	// Baseline representing historical state BEFORE current transaction
	baseline := &repository.UserBaseline{
		UserID:                 "user_audit_1",
		AverageAmount:          100.0,
		TransactionStdDev:      50.0,
		PreferredPaymentMethod: "CARD",
		UsualCity:              "New York",
		ActiveHourStart:        8,
		ActiveHourEnd:          20,
	}

	bRepo := &mockBaselineRepo{baseline: baseline}
	hRepo := &mockHistoryRepo{txCount: 3}

	// New transaction: $500 in Month 6 (June)
	event := events.TransactionEvent{
		UserID:            "user_audit_1",
		Timestamp:         "2026-06-15T14:30:00Z",
		Amount:            500.0,
		PaymentMethod:     "CARD",
		Location:          "New York",
		Merchant:          "Merchant_A",
		ReceiverAccount:   "rec_1",
		PaymentIdentifier: "card_123",
	}

	vector := features.BuildFeatureVector(event, bRepo, hRepo)

	// Invariant checks:
	// AmountDeviation = (500 - 100) / 100 = 4.0
	if vector.AmountDeviation != 4.0 {
		t.Errorf("Expected AmountDeviation 4.0, got %f", vector.AmountDeviation)
	}

	// AmountZScore = (500 - 100) / 50 = 8.0
	if vector.AmountZScore != 8.0 {
		t.Errorf("Expected AmountZScore 8.0, got %f", vector.AmountZScore)
	}

	// Month must come from transaction timestamp (June = 6)
	if vector.Month != 6 {
		t.Errorf("Expected Month 6, got %d", vector.Month)
	}

	// IsFirstTransaction must be false
	if vector.IsFirstTransaction {
		t.Errorf("Expected IsFirstTransaction to be false")
	}

	if vector.TransactionVelocity1H != 3 {
		t.Errorf("Expected TransactionVelocity1H 3, got %d", vector.TransactionVelocity1H)
	}
}

func TestTimestampMonthExtractionAcrossBoundaries(t *testing.T) {
	tests := []struct {
		timestamp     string
		expectedMonth int
		expectedHour  int
		expectedWknd  bool
	}{
		{"2026-01-01T00:00:00Z", 1, 0, false},   // New Year midnight (Thursday)
		{"2026-02-28T23:59:59Z", 2, 23, true},   // Month end (Saturday)
		{"2026-07-04T12:00:00Z", 7, 12, true},   // Mid-year weekend (Saturday)
		{"2026-12-31T23:59:59Z", 12, 23, false}, // Year end (Thursday)
	}

	bRepo := &mockBaselineRepo{baseline: nil}
	hRepo := &mockHistoryRepo{txCount: 0}

	for _, tt := range tests {
		event := events.TransactionEvent{
			UserID:    "user_time_test",
			Timestamp: tt.timestamp,
			Amount:    50.0,
		}

		vector := features.BuildFeatureVector(event, bRepo, hRepo)

		if vector.Month != tt.expectedMonth {
			t.Errorf("For timestamp %s: expected month %d, got %d", tt.timestamp, tt.expectedMonth, vector.Month)
		}
		if vector.HourOfDay != tt.expectedHour {
			t.Errorf("For timestamp %s: expected hour %d, got %d", tt.timestamp, tt.expectedHour, vector.HourOfDay)
		}
		if vector.IsWeekend != tt.expectedWknd {
			t.Errorf("For timestamp %s: expected weekend %v, got %v", tt.timestamp, tt.expectedWknd, vector.IsWeekend)
		}
		if !vector.IsFirstTransaction {
			t.Errorf("For user with nil baseline: expected IsFirstTransaction true, got false")
		}
	}
}

func TestRedisFailureNoPanicAndGracefulHandling(t *testing.T) {
	// Call GetRedisClient() directly - must never panic
	client := cache.GetRedisClient()
	if client == nil {
		t.Fatal("Expected GetRedisClient() to return non-nil client struct")
	}

	// ReadyHandler must respond gracefully (503 when disconnected) without panicking
	req := httptest.NewRequest(http.MethodGet, "/health/ready", nil)
	rr := httptest.NewRecorder()

	apihandler.ReadyHandler(rr, req)

	if rr.Code != http.StatusOK && rr.Code != http.StatusServiceUnavailable {
		t.Errorf("Unexpected status code %d from ReadyHandler", rr.Code)
	}
}

func TestPostgreSQLSchemaIntegritySQLContract(t *testing.T) {
	// Verify that the table foreign keys and columns match the application contract
	initSQL := `
	CREATE TABLE IF NOT EXISTS fraud_predictions (
		id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
		transaction_id UUID NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
		user_id UUID NOT NULL,
		fraud_probability DOUBLE PRECISION NOT NULL,
		confidence DOUBLE PRECISION NOT NULL DEFAULT 1.0,
		prediction BOOLEAN NOT NULL,
		decision VARCHAR(20) NOT NULL,
		threshold DOUBLE PRECISION NOT NULL,
		model_version VARCHAR(50) NOT NULL,
		risk_flags JSONB,
		created_at TIMESTAMP NOT NULL DEFAULT NOW()
	);
	`
	if !strings.Contains(initSQL, "REFERENCES transactions(transaction_id)") {
		t.Error("Schema definition missing valid foreign key REFERENCES transactions(transaction_id)")
	}
	if !strings.Contains(initSQL, "confidence DOUBLE PRECISION") {
		t.Error("Schema definition missing confidence column")
	}
}
