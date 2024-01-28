CREATE TABLE session
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee_id      UUID NOT NULL,
    end_time         TIMESTAMPTZ DEFAULT NULL,
    FOREIGN KEY (employee_id) REFERENCES user_accounts (id),
    CONSTRAINT session_end_time_check CHECK (end_time IS NULL OR end_time >= created_at),
    INDEX session_employee_id_idx (employee_id)
);