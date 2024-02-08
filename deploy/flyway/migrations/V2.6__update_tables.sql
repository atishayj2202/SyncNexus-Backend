ALTER TABLE employee_mapping
    ADD COLUMN title VARCHAR NOT NULL default 'Employee';

ALTER TABLE user_accounts
    ADD COLUMN email VARCHAR UNIQUE NULL default NULL;