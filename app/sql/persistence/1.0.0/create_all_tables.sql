
-- Drop tables if they exist to ensure a clean slate

DROP TABLE IF EXISTS audit_script CASCADE;
DROP TABLE IF EXISTS variable CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

CREATE TABLE audit_script (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    process VARCHAR(50) NOT NULL,
    version VARCHAR(10) NOT NULL,
    schema VARCHAR(50) NOT NULL
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    ip VARCHAR(20) NOT NULL,
    p_timer_communication_cycle INTEGER,
    production_order_code VARCHAR(20)
);

CREATE TABLE variable (
    id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL REFERENCES equipment(id),
    key VARCHAR(20) NOT NULL,
    offset_byte INTEGER NOT NULL,
    offset_bit INTEGER NOT NULL,
    db_address INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    operation_type VARCHAR(10) NOT NULL CHECK (operation_type IN ('READ', 'WRITE')),
    category VARCHAR(10),
    value JSONB
);
