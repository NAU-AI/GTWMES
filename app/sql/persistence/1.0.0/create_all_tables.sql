-- Drop tables if they exist to ensure a clean slate
DROP TABLE IF EXISTS audit_script CASCADE;
DROP TABLE IF EXISTS counter_record CASCADE;
DROP TABLE IF EXISTS active_time_record CASCADE;
DROP TABLE IF EXISTS alarm_record CASCADE;
DROP TABLE IF EXISTS production_order CASCADE;
DROP TABLE IF EXISTS equipment_output CASCADE;
DROP TABLE IF EXISTS variable CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

-- Create tables
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
    p_timer_communication_cycle INTEGER
);

CREATE TABLE variable (
    id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL REFERENCES equipment(id),
    key VARCHAR(20) NOT NULL,
    offset_byte INTEGER NOT NULL,
    offset_bit INTEGER NOT NULL,
    db_address VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL,
    operation_type VARCHAR(10) NOT NULL CHECK (operation_type IN ('READ', 'WRITE'))
);

CREATE TABLE equipment_output (
    id SERIAL PRIMARY KEY,
    equipment_id INT NOT NULL REFERENCES equipment(id),
    variable_id INTEGER REFERENCES variable(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL
);

CREATE TABLE production_order (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    is_completed BOOLEAN NOT NULL
);

CREATE TABLE active_time_record (
    id SERIAL PRIMARY KEY,
    variable INTEGER REFERENCES variable(id) ON DELETE CASCADE,
    active_time INTEGER NOT NULL,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE counter_record (
    id SERIAL PRIMARY KEY,
    equipment_output_id INTEGER REFERENCES equipment_output(id) ON DELETE CASCADE,
    real_value INTEGER NOT NULL,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alarm_record (
    id SERIAL PRIMARY KEY,
    variable INTEGER REFERENCES variable(id) ON DELETE CASCADE,
    value INTEGER NOT NULL,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
