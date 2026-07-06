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

	query := `
	INSERT INTO transactions (
		user_id,
		amount,
		currency,
		payment_method,
		payment_identifier,
		merchant,
		receiver_account,
		location,
		ip_address,
		device_id,
		status
	)
	VALUES (
		$1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11
	)
	RETURNING transaction_id;
	`

	var transactionID string

	err := r.db.QueryRowContext(
		ctx,
		query,
		transaction.UserId,
		transaction.Amount,
		transaction.Currency,
		transaction.PaymentMethod,
		transaction.PaymentIdentifier,
		transaction.Merchant,
		transaction.ReceiverAccount,
		transaction.Location,
		transaction.IpAddress,
		transaction.DeviceId,
		"PENDING",
	).Scan(&transactionID)

	if err != nil {
		return "", err
	}

	return transactionID, nil
}