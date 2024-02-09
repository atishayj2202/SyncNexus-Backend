CREATE TABLE employee_mapping
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee_id      UUID NOT NULL,
    employer_id      UUID NOT NULL,
    deleted          TIMESTAMPTZ DEFAULT NULL,
    FOREIGN KEY (employee_id) REFERENCES user_accounts (id),
    FOREIGN KEY (employer_id) REFERENCES user_accounts (id)
);

CREATE INDEX idx_employee ON employee_mapping(employee_id);
CREATE INDEX idx_employer_mapping ON employee_mapping(employer_id);