package handler

import (
	"context"
	"encoding/json"
	"net/http"

	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/service"
)

type TransactionHandler struct {
	service *service.TransactionService
}

func NewTransactionHandler(
	service *service.TransactionService,
) *TransactionHandler {

	return &TransactionHandler{
		service: service,
	}
}

func (h *TransactionHandler) SubmitTransaction(
	w http.ResponseWriter,
	r *http.Request,
) {

	if r.Method != http.MethodPost {
		http.Error(
			w,
			"Method not allowed",
			http.StatusMethodNotAllowed,
		)
		return
	}

	var req pb.TransactionRequest

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(
			w,
			err.Error(),
			http.StatusBadRequest,
		)
		return
	}

	resp, err := h.service.SubmitTransaction(
		context.Background(),
		&req,
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

	json.NewEncoder(w).Encode(resp)
}