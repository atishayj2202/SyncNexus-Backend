CREATE TABLE employee_location
(
    id               UUID PRIMARY KEY,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    last_modified_at TIMESTAMPTZ DEFAULT NOW(),
    session_id       UUID NOT NULL,
    location         GEOGRAPHY(Point),
    FOREIGN KEY (session_id) REFERENCES session (id),
    INDEX idx_location_session (session_id)
)