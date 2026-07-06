package postgres

import (
	"context"
	"database/sql"

	pb "github.com/Vaibhav20k/fintech-pipeline/ingestion-gateway/proto"
)

type TransactionRepository struct {
	db *sql.DB
}

func NewTransactionRepository(
	db *sql.DB,
) *TransactionRepository {

	return &TransactionRepository{
		db: db,
	}
}

func (r *TransactionRepository) SaveTransaction(
	ctx context.Context,
	transaction *pb.TransactionRequest,
) (string, error) {

	// SQL implementation will be added next.

	return "txn-demo-001", nil
}