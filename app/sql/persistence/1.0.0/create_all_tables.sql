BEGIN;

DROP TABLE IF EXISTS counting_equipment CASCADE;
DROP TABLE IF EXISTS equipment_output CASCADE;
DROP TABLE IF EXISTS production_order CASCADE;
DROP TABLE IF EXISTS active_time CASCADE;
DROP TABLE IF EXISTS alarm CASCADE;
DROP TABLE IF EXISTS counter_record CASCADE;
DROP TABLE IF EXISTS audit_script CASCADE;

CREATE TABLE counting_equipment (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    equipment_status INTEGER,
    p_timer_communication_cycle INTEGER,
    plc_ip VARCHAR(20) NOT NULL DEFAULT '0'
);

CREATE TABLE equipment_output (
    id SERIAL PRIMARY KEY,
    counting_equipment_id INTEGER REFERENCES counting_equipment(id),
    code VARCHAR(20) NOT NULL
);

CREATE TABLE production_order (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES counting_equipment(id),
    code VARCHAR(20),
    is_completed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE active_time (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES counting_equipment(id),
    active_time INTEGER,
    registered_at TIMESTAMP
);

CREATE TABLE alarm (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES counting_equipment(id),
    alarm_0 INTEGER,
    alarm_1 INTEGER,
    alarm_2 INTEGER,
    alarm_3 INTEGER,
    registered_at TIMESTAMP
);

CREATE TABLE counter_record (
    id SERIAL PRIMARY KEY,
    equipment_output_id INTEGER REFERENCES equipment_output(id),
    real_value INTEGER,
    registered_at TIMESTAMP
);

CREATE TABLE audit_script (
    id SERIAL PRIMARY KEY,
    run_date DATE NOT NULL,
    process VARCHAR(50) NOT NULL,
    version VARCHAR(10) NOT NULL,
    schema VARCHAR(50) NOT NULL
);

CREATE TABLE equipment_variable (
    id SERIAL PRIMARY KEY,
    counting_equipment_id INTEGER NOT NULL,
    name VARCHAR(20) NOT NULL,
    db_address VARCHAR(20) NOT NULL,
    offset_byte INTEGER NOT NULL,
    offset_bit INTEGER NOT NULL DEFAULT 0,
    type VARCHAR(20) NOT NULL,
    FOREIGN KEY (counting_equipment_id) REFERENCES counting_equipment(id)
);

COMMIT;
