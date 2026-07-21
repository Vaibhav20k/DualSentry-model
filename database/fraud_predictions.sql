CREATE TABLE IF NOT EXISTS fraud_predictions (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_id UUID NOT NULL
        REFERENCES transactions(transaction_id)
        ON DELETE CASCADE,

    user_id UUID NOT NULL,

    fraud_probability DOUBLE PRECISION NOT NULL,

    confidence DOUBLE PRECISION NOT NULL,

    prediction BOOLEAN NOT NULL,

    decision VARCHAR(20) NOT NULL,

    threshold DOUBLE PRECISION NOT NULL,

    model_version VARCHAR(50) NOT NULL,

    risk_flags JSONB,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_transaction
ON fraud_predictions(transaction_id);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_user
ON fraud_predictions(user_id);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_decision
ON fraud_predictions(decision);

CREATE INDEX IF NOT EXISTS idx_fraud_predictions_created_at
ON fraud_predictions(created_at DESC);