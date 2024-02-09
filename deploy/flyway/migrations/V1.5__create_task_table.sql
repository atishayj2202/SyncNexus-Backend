CREATE TABLE task
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee_id      UUID    NOT NULL,
    employer_id      UUID    NOT NULL,
    heading          VARCHAR NOT NULL,
    description      TEXT        DEFAULT NULL,
    last_date        TIMESTAMPTZ DEFAULT NULL,
    deleted          TIMESTAMPTZ DEFAULT NULL,
    completed        TIMESTAMPTZ DEFAULT NULL,
    FOREIGN KEY (employee_id) REFERENCES user_accounts (id),
    FOREIGN KEY (employer_id) REFERENCES user_accounts (id),
    CHECK (last_date IS NULL OR last_date > NOW())
);

CREATE INDEX idx_task_employee ON task(employee_id);
CREATE INDEX idx_task_employer ON task(employer_id)