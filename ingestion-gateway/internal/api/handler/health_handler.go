package handler

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/cache"
)

type HealthResponse struct {
	Status string `json:"status"`
}

func LiveHandler(
	w http.ResponseWriter,
	r *http.Request,
) {

	w.Header().Set(
		"Content-Type",
		"application/json",
	)

	json.NewEncoder(w).Encode(
		HealthResponse{
			Status: "UP",
		},
	)
}

func ReadyHandler(
	w http.ResponseWriter,
	r *http.Request,
) {

	ctx := context.Background()

	// Redis readiness check
	client := cache.GetRedisClient()

	if err := client.Ping(ctx).Err(); err != nil {

		http.Error(
			w,
			"Redis unavailable",
			http.StatusServiceUnavailable,
		)

		return
	}

	w.Header().Set(
		"Content-Type",
		"application/json",
	)

	json.NewEncoder(w).Encode(
		HealthResponse{
			Status: "READY",
		},
	)
}
