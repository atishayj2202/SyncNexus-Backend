CREATE TABLE rating
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    user_from        UUID                                NOT NULL,
    user_to          UUID                                NOT NULL,
    rate             INT CHECK (rate >= 1 AND rate <= 5) NOT NULL,
    comment          TEXT        DEFAULT NULL,
    FOREIGN KEY (user_from) REFERENCES user_accounts (id),
    FOREIGN KEY (user_to) REFERENCES user_accounts (id),
    CONSTRAINT unique_rating UNIQUE (user_from, user_to)
);
CREATE INDEX idx_rating_to ON rating(user_to);