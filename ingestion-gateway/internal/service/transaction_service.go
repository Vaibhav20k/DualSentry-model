package service

import (
	"context"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"

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
	event := events.TransactionEvent{
	TransactionID:     transactionID,
	UserID:            req.UserId,
	Amount:            req.Amount,
	Currency:          req.Currency,
	PaymentMethod:     req.PaymentMethod,
	PaymentIdentifier: req.PaymentIdentifier,
	Merchant:          req.Merchant,
	ReceiverAccount:   req.ReceiverAccount,
	Location:          req.Location,
	IPAddress:         req.IpAddress,
	DeviceID:          req.DeviceId,
	Status:            "RECEIVED",
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
