-- =====================================================
-- Fintech Pipeline Database Initialization
-- =====================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- Transactions Table
-- =====================================================
CREATE TABLE transactions (

    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID NOT NULL,

    amount DECIMAL(12,2) NOT NULL
        CHECK (amount > 0),

    currency VARCHAR(3) NOT NULL
        DEFAULT 'INR',

    payment_method VARCHAR(20) NOT NULL
        CHECK (
            payment_method IN (
                'UPI',
                'CARD',
                'NET_BANKING',
                'WALLET'
            )
        ),

    payment_identifier VARCHAR(255),

    merchant VARCHAR(255) NOT NULL,

    receiver_account VARCHAR(255),

    location VARCHAR(255),

    ip_address INET,

    device_id VARCHAR(255),

    status VARCHAR(20) NOT NULL
        CHECK (
            status IN (
                'PENDING',
                'SUCCESS',
                'FAILED'
            )
        ),

    created_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- User Behaviour Baseline Table
-- =====================================================
CREATE TABLE user_baselines (

    user_id UUID PRIMARY KEY,

    average_transaction_amount DECIMAL(12,2) NOT NULL
        CHECK (average_transaction_amount >= 0),

    transaction_amount_stddev DECIMAL(12,2) NOT NULL
        CHECK (transaction_amount_stddev >= 0),

    average_daily_transactions INTEGER NOT NULL
        CHECK (average_daily_transactions >= 0),

    preferred_payment_method VARCHAR(20)
        CHECK (
            preferred_payment_method IN (
                'UPI',
                'CARD',
                'NET_BANKING',
                'WALLET'
            )
        ),

    preferred_merchant_category VARCHAR(100),

    usual_city VARCHAR(100),

    active_hours_start SMALLINT
        CHECK (active_hours_start BETWEEN 0 AND 23),

    active_hours_end SMALLINT
        CHECK (active_hours_end BETWEEN 0 AND 23),

    last_updated TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- Anomaly Logs Table
-- =====================================================
CREATE TABLE anomaly_logs (

    anomaly_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    transaction_id UUID NOT NULL,

    anomaly_score DECIMAL(5,4) NOT NULL
        CHECK (anomaly_score BETWEEN 0 AND 1),

    anomaly_type VARCHAR(50),

    model_name VARCHAR(100) NOT NULL,

    model_version VARCHAR(50) NOT NULL,

    explanation TEXT,

    detected_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);
-- -- ==========================================================
-- -- Fraud Predictions
-- -- ==========================================================

-- CREATE TABLE IF NOT EXISTS fraud_predictions (

--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

--     transaction_id UUID NOT NULL
--         REFERENCES transactions(id)
--         ON DELETE CASCADE,

--     user_id UUID NOT NULL,

--     fraud_probability DOUBLE PRECISION NOT NULL,

--     prediction BOOLEAN NOT NULL,

--     decision VARCHAR(20) NOT NULL,

--     threshold DOUBLE PRECISION NOT NULL,

--     model_version VARCHAR(50) NOT NULL,

--     risk_flags JSONB,

--     created_at TIMESTAMP NOT NULL DEFAULT NOW()
-- );

-- CREATE INDEX IF NOT EXISTS idx_fraud_predictions_transaction
-- ON fraud_predictions(transaction_id);

-- CREATE INDEX IF NOT EXISTS idx_fraud_predictions_user
-- ON fraud_predictions(user_id);

-- CREATE INDEX IF NOT EXISTS idx_fraud_predictions_decision
-- ON fraud_predictions(decision);

-- CREATE INDEX IF NOT EXISTS idx_fraud_predictions_created_at
-- ON fraud_predictions(created_at DESC);

-- ============================================
-- Manual Review Queue
-- ============================================

CREATE TABLE IF NOT EXISTS manual_review_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_id UUID NOT NULL
        REFERENCES transactions(id)
        ON DELETE CASCADE,

    fraud_probability DECIMAL(6,5) NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Fraud Alerts
-- ============================================

CREATE TABLE IF NOT EXISTS fraud_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    transaction_id UUID NOT NULL
        REFERENCES transactions(id)
        ON DELETE CASCADE,

    fraud_probability DECIMAL(6,5) NOT NULL,

    alert_type VARCHAR(30) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);