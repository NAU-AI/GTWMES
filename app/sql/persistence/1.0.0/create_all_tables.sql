-- Drop tables
DROP TABLE IF EXISTS counting_equipment;
DROP TABLE IF EXISTS equipment_output;
DROP TABLE IF EXISTS production_order;
DROP TABLE IF EXISTS active_time;
DROP TABLE IF EXISTS alarm;
DROP TABLE IF EXISTS counter_record;
DROP TABLE IF EXISTS audit_script;

-- Create table counting_equipment
CREATE TABLE counting_equipment (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    equipment_status INTEGER,
    p_timer_communication_cycle INTEGER
);

-- Create table equipment_output
CREATE TABLE equipment_output (
    id SERIAL PRIMARY KEY,
    equipment_code VARCHAR(20) NOT NULL,
    code VARCHAR(20) NOT NULL,
    disable INTEGER NOT NULL
);

-- Create table production_order
CREATE TABLE production_order (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES counting_equipment(id),
    code VARCHAR(20) NOT NULL,
    finished INTEGER NOT NULL DEFAULT 0
);

-- Create table active_time
CREATE TABLE active_time (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES counting_equipment(id),
    active_time INTEGER,
    registered_at TIMESTAMP
);

-- Create table alarm
CREATE TABLE alarm (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES counting_equipment(id),
    alarm_1 INTEGER,
    alarm_2 INTEGER,
    alarm_3 INTEGER,
    alarm_4 INTEGER,
    registered_at TIMESTAMP
);

-- Create table counter_record
CREATE TABLE counter_record (
    id SERIAL PRIMARY KEY,
    equipment_output_id INTEGER REFERENCES equipment_output(id),
    real_value INTEGER,
    registered_at TIMESTAMP
);

-- Create table audit_script
CREATE TABLE audit_script (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    process VARCHAR(50) NOT NULL,
    version VARCHAR(10) NOT NULL,
    schema VARCHAR(50) NOT NULL
);