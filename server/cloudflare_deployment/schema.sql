-- D1 Database Schema for Token Detector
-- Migration script to create tables for token analysis data

CREATE TABLE IF NOT EXISTS token_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT NOT NULL,
    name TEXT,
    symbol TEXT,
    score_normalised INTEGER,
    risk_level TEXT,
    price REAL,
    holders INTEGER,
    liquidity REAL,
    market_cap REAL,
    creator_holdings_pct REAL,
    detected_at TEXT,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_json TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_token_reports_token_id ON token_reports(token_id);
CREATE INDEX IF NOT EXISTS idx_token_reports_fetched_at ON token_reports(fetched_at);
CREATE INDEX IF NOT EXISTS idx_token_reports_token_id_fetched_at ON token_reports(token_id, fetched_at);
CREATE INDEX IF NOT EXISTS idx_token_reports_risk_level ON token_reports(risk_level);

-- Create a view for recent tokens
CREATE VIEW IF NOT EXISTS recent_tokens AS
SELECT 
    id,
    token_id,
    name,
    symbol,
    risk_level,
    score_normalised,
    price,
    market_cap,
    liquidity,
    holders,
    creator_holdings_pct,
    detected_at,
    fetched_at
FROM token_reports
ORDER BY fetched_at DESC;
