CREATE TABLE employee_mapping
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee_id      UUID NOT NULL,
    employer_id      UUID NOT NULL,
    deleted          TIMESTAMPTZ DEFAULT NULL,
    INDEX idx_employee (employee_id),
    INDEX idx_employer (employer_id),
    FOREIGN KEY (employee_id) REFERENCES user_accounts (id),
    FOREIGN KEY (employer_id) REFERENCES user_accounts (id)
);