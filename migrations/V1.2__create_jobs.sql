CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employer UUID NOT NULL,
    deleted TIMESTAMPTZ DEFAULT NULL,
    location GEOGRAPHY(Point),
    done TIMESTAMPTZ DEFAULT NULL,
    amount BIGINT,
    FOREIGN KEY (employer) REFERENCES user_accounts(id)
);