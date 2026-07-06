package service

import (
	"context"

	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/events"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/kafka"
	"github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/internal/repository"
	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"
)

type TransactionService struct {
	repository repository.TransactionRepository
	producer   *kafka.Producer
	updater    *BaselineUpdater
}

func NewTransactionService(
	repo repository.TransactionRepository,
	producer *kafka.Producer,
	updater *BaselineUpdater,
) *TransactionService {

	return &TransactionService{
		repository: repo,
		producer:   producer,
		updater:    updater,
	}
}

func (s *TransactionService) SubmitTransaction(
	ctx context.Context,
	req *pb.TransactionRequest,
) (*pb.TransactionResponse, error) {

	// Step 1: Persist transaction
	transactionID, err := s.repository.SaveTransaction(ctx, req)
	if err != nil {
		return nil, err
	}

	// Step 2: Update user baseline
	if s.updater != nil {
		if err := s.updater.UpdateBaseline(ctx, req.UserId); err != nil {
			return nil, err
		}
	}

	// Step 3: Publish Kafka event
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

	if err := s.producer.PublishJSON(transactionID, event); err != nil {
		return nil, err
	}

	return &pb.TransactionResponse{
		TransactionId: transactionID,
		Status:        "RECEIVED",
		Message:       "Transaction stored successfully.",
	}, nil
}