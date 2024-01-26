CREATE TABLE Task (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee UUID NOT NULL,
    employer UUID NOT NULL,
    heading VARCHAR NOT NULL,
    text TEXT DEFAULT NULL,
    last_date TIMESTAMPTZ DEFAULT NULL,
    deleted TIMESTAMPTZ DEFAULT NULL,
    completed TIMESTAMPTZ DEFAULT NULL,
    FOREIGN KEY (employee) REFERENCES user_accounts(id),
    FOREIGN KEY (employer) REFERENCES user_accounts(id),
    CHECK (last_date IS NULL OR last_date > NOW()),
    INDEX idx_task_employee (employee),
    INDEX idx_task_employer (employer)
);
