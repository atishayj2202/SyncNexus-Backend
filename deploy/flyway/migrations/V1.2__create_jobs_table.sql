CREATE TABLE jobs
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employer_id      UUID    NOT NULL,
    title            VARCHAR NOT NULL,
    description      TEXT,
    deleted          TIMESTAMPTZ DEFAULT NULL,
    location_lat     NUMERIC NOT NULL,
    location_long    NUMERIC NOT NULL,
    done             TIMESTAMPTZ DEFAULT NULL,
    amount           BIGINT,
    FOREIGN KEY (employer_id) REFERENCES user_accounts (id)
);
CREATE INDEX idx_jobs_location ON jobs (location_lat, location_long);
CREATE INDEX idx_employer ON jobs (employer_id);