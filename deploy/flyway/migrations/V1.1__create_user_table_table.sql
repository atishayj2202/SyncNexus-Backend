CREATE TYPE user_type AS ENUM ('employee', 'employer');

CREATE TABLE user_accounts
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT now()::TIMESTAMPTZ,
    last_modified_at TIMESTAMPTZ DEFAULT now()::TIMESTAMPTZ,
    phone_no         VARCHAR   NOT NULL,
    name             VARCHAR   NOT NULL,
    firebase_user_id VARCHAR   NOT NULL,
    user_type        user_type NOT NULL,
    UNIQUE (firebase_user_id),
    UNIQUE (phone_no)
);

CREATE INDEX idx_firebase_user_id ON user_accounts(firebase_user_id);
CREATE INDEX idx_phone_no ON user_accounts(phone_no)