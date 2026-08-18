package handler

import (
	"encoding/json"
	"net/http"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/cache"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

type DashboardHandler struct {
	repository repository.FraudPredictionRepository
}

func NewDashboardHandler(
	repository repository.FraudPredictionRepository,
) *DashboardHandler {

	return &DashboardHandler{
		repository: repository,
	}
}

func (h *DashboardHandler) GetSummary(
	w http.ResponseWriter,
	r *http.Request,
) {

	ctx := r.Context()

	var summary any

	found, err := cache.GetDashboardSummary(
		ctx,
		&summary,
	)

	if err == nil && found {

		w.Header().Set(
			"Content-Type",
			"application/json",
		)

		json.NewEncoder(w).Encode(summary)
		return
	}

	summary, err = h.repository.GetDashboardSummary(ctx)
	if err != nil {

		http.Error(
			w,
			err.Error(),
			http.StatusInternalServerError,
		)

		return
	}

	_ = cache.SetDashboardSummary(
		ctx,
		summary,
	)

	w.Header().Set(
		"Content-Type",
		"application/json",
	)

	json.NewEncoder(w).Encode(summary)
}

func (h *DashboardHandler) GetTrend(
	w http.ResponseWriter,
	r *http.Request,
) {

	ctx := r.Context()

	var trend any

	found, err := cache.GetDashboardTrend(
		ctx,
		&trend,
	)

	if err == nil && found {

		w.Header().Set(
			"Content-Type",
			"application/json",
		)

		json.NewEncoder(w).Encode(trend)
		return
	}

	trend, err = h.repository.GetFraudTrend(ctx)
	if err != nil {

		http.Error(
			w,
			err.Error(),
			http.StatusInternalServerError,
		)

		return
	}

	_ = cache.SetDashboardTrend(
		ctx,
		trend,
	)

	w.Header().Set(
		"Content-Type",
		"application/json",
	)

	json.NewEncoder(w).Encode(trend)
}
