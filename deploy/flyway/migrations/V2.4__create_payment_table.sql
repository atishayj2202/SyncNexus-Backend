CREATE TABLE payments
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    approved_at      TIMESTAMPTZ DEFAULT NULL,
    amount           INT                       NOT NULL,
    currency         TEXT        DEFAULT 'INR' NOT NULL,
    remarks          TEXT        DEFAULT NULL,
    from_user_id     UUID                      NOT NULL,
    to_user_id       UUID                      NOT NULL,
    FOREIGN KEY (from_user_id) REFERENCES user_accounts (id),
    FOREIGN KEY (to_user_id) REFERENCES user_accounts (id),
    CHECK (amount > 0)
);

CREATE INDEX payments_from_user_id_idx ON payments (from_user_id);
CREATE INDEX payments_to_user_id_idx ON payments (to_user_id);