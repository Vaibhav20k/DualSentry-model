package handler_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	apihandler "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/api/handler"
)

func TestLiveHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health/live", nil)
	rr := httptest.NewRecorder()

	apihandler.LiveHandler(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("LiveHandler returned %d, want %d", rr.Code, http.StatusOK)
	}

	var body map[string]interface{}
	if err := json.NewDecoder(rr.Body).Decode(&body); err != nil {
		t.Fatalf("failed to decode response: %v", err)
	}

	if body["status"] == nil {
		t.Error("expected 'status' field in response body")
	}
}

func TestReadyHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health/ready", nil)
	rr := httptest.NewRecorder()

	apihandler.ReadyHandler(rr, req)

	if rr.Code != http.StatusOK {
		t.Errorf("ReadyHandler returned %d, want %d", rr.Code, http.StatusOK)
	}
}
