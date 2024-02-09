CREATE TABLE feedbacks
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    rating           INT  NOT NULL,
    feedback         TEXT        DEFAULT NULL,
    from_user_id     UUID NOT NULL,
    FOREIGN KEY (from_user_id) REFERENCES user_accounts (id),
    CHECK (rating > 0)
);

CREATE INDEX feedbacks_from_user_id_idx ON feedbacks (from_user_id);