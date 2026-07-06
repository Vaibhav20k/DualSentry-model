package service

import (
	"context"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"

)

type TransactionService struct {
	repository repository.TransactionRepository

	producer   *kafka.Producer
}

func NewTransactionService(
	repo repository.TransactionRepository,
	producer *kafka.Producer,
) *TransactionService {

	return &TransactionService{
		repository: repo,
		producer:   producer,
	}
}

func (s *TransactionService) SubmitTransaction(
	ctx context.Context,
	req *pb.TransactionRequest,
) (*pb.TransactionResponse, error) {

	transactionID, err := s.repository.SaveTransaction(ctx, req)
	if err != nil {
		return nil, err
	}
	event := map[string]interface{}{
		"transaction_id": transactionID,
		"user_id":        req.UserId,
		"amount":         req.Amount,
		"currency":       req.Currency,
		"payment_method": req.PaymentMethod,
		"merchant":       req.Merchant,
		"status":         "RECEIVED",
	}

	err = s.producer.PublishJSON(
		transactionID,
		event,
	)
	if err != nil {
		return nil, err
	}

	return &pb.TransactionResponse{
		TransactionId: transactionID,
		Status:        "RECEIVED",
		Message:       "Transaction stored successfully.",
	}, nil
}
