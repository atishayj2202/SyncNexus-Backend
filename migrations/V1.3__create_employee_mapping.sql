CREATE TABLE your_table_name (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee UUID NOT NULL,
    employer UUID NOT NULL,
    is_deleted TIMESTAMPTZ DEFAULT NULL,
    FOREIGN KEY (employee) REFERENCES user_accounts(id),
    FOREIGN KEY (employer) REFERENCES user_accounts(id),
);