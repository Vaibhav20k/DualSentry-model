package repository

import (
	"context"

	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"
)

type TransactionRepository interface {
	SaveTransaction(
		ctx context.Context,
		transaction *pb.TransactionRequest,
	) (string, error)
}
