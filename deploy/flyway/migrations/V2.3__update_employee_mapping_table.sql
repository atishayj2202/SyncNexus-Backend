CREATE TYPE employee_map_type AS ENUM ('active', 'left', 'removed');

ALTER TABLE employee_mapping
    ADD COLUMN status employee_map_type DEFAULT 'active';
