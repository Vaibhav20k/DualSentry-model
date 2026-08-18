package handler

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
)

type PredictionHandler struct {
	repository repository.FraudPredictionRepository
}

func NewPredictionHandler(
	repository repository.FraudPredictionRepository,
) *PredictionHandler {

	return &PredictionHandler{
		repository: repository,
	}
}

func (h *PredictionHandler) GetAllPredictions(
	w http.ResponseWriter,
	r *http.Request,
) {

	predictions, err := h.repository.GetAllPredictions(
		context.Background(),
	)

	if err != nil {

		http.Error(
			w,
			err.Error(),
			http.StatusInternalServerError,
		)

		return
	}

	w.Header().Set(
		"Content-Type",
		"application/json",
	)

	json.NewEncoder(w).Encode(predictions)
}
