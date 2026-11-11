PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS cheque_deposits;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS demo_issuers;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number       TEXT NOT NULL UNIQUE,
    holder_name          TEXT NOT NULL,
    account_type         TEXT NOT NULL CHECK (account_type IN ('Savings', 'Current')),
    balance_paise        INTEGER NOT NULL DEFAULT 0 CHECK (balance_paise >= 0),
    pin_hash             TEXT NOT NULL,
    failed_attempts      INTEGER NOT NULL DEFAULT 0,
    locked_until         TEXT,
    passbook_last_txn_id INTEGER NOT NULL DEFAULT 0,
    is_active            INTEGER NOT NULL DEFAULT 1,
    created_at           TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE transactions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_no        TEXT NOT NULL UNIQUE,
    account_id          INTEGER NOT NULL,
    txn_date            TEXT NOT NULL,
    txn_type            TEXT NOT NULL CHECK (txn_type IN ('CREDIT', 'DEBIT')),
    channel             TEXT NOT NULL,
    description         TEXT NOT NULL,
    amount_paise        INTEGER NOT NULL CHECK (amount_paise > 0),
    balance_after_paise INTEGER NOT NULL CHECK (balance_after_paise >= 0),
    status              TEXT NOT NULL DEFAULT 'COMPLETED' CHECK (status IN ('COMPLETED')),
    created_at          TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);

CREATE TABLE demo_issuers (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    issuer_account_no TEXT NOT NULL UNIQUE,
    issuer_name       TEXT NOT NULL
);

CREATE TABLE cheque_deposits (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_no       TEXT NOT NULL UNIQUE,
    account_id         INTEGER NOT NULL,
    transaction_id     INTEGER,
    cheque_number      TEXT,
    cheque_date        TEXT,
    issuer_account_no  TEXT,
    payee_name         TEXT,
    amount_paise       INTEGER CHECK (amount_paise IS NULL OR amount_paise >= 0),
    image_filename     TEXT,
    ocr_raw_text       TEXT,
    was_edited_by_user INTEGER NOT NULL DEFAULT 0,
    status             TEXT NOT NULL CHECK (status IN ('APPROVED_SIMULATED', 'REJECTED_SIMULATED')),
    rejection_reasons  TEXT,
    created_at         TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (account_id) REFERENCES accounts (id),
    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
);

CREATE TABLE admin (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX idx_txn_account_date ON transactions (account_id, txn_date);
CREATE INDEX idx_cheque_account ON cheque_deposits (account_id);