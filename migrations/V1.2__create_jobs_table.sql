CREATE TABLE jobs
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employer_id      UUID NOT NULL,
    deleted          TIMESTAMPTZ DEFAULT NULL,
    location         GEOGRAPHY(Point),
    done             TIMESTAMPTZ DEFAULT NULL,
    amount           BIGINT,
    FOREIGN KEY (employer_id) REFERENCES user_accounts (id),
    INDEX idx_jobs_location (location),
    INDEX idx_employer (employer_id)
);