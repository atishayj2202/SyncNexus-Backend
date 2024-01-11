CREATE TYPE auth_type AS ENUM ('google', 'github', 'facebook', 'apple');

CREATE TABLE user_accounts (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now()::TIMESTAMPTZ,
    last_modified_at TIMESTAMPTZ DEFAULT now()::TIMESTAMPTZ,
    email VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    firebase_user_id VARCHAR NOT NULL,
    auth_type auth_type NOT NULL,
    UNIQUE(firebase_user_id),
    UNIQUE(email),
    INDEX idx_firebase_user_id (firebase_user_id),
    INDEX idx_email (email)
);
