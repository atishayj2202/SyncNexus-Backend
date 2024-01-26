CREATE TABLE rating (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    "from" UUID NOT NULL,
    "to" UUID NOT NULL ,
    rate INT CHECK (rate >= 1 AND rate <= 5) NOT NULL,
    comment TEXT DEFAULT NULL,
    FOREIGN KEY ("from") REFERENCES user_accounts (id),
    FOREIGN KEY ("to") REFERENCES user_accounts (id),
    CONSTRAINT unique_rating UNIQUE ("from", "to"),
    INDEX idx_rating_to ("to")
);