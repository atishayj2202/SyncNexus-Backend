CREATE TABLE employee_location
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    employee_id      UUID    NOT NULL,
    location_lat     NUMERIC NOT NULL,
    location_long    NUMERIC NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES user_accounts (id)
);

CREATE INDEX idx_location_session ON employee_location(employee_id);