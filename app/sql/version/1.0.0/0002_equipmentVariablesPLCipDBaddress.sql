ALTER TABLE counting_equipment
ADD COLUMN plc_ip VARCHAR(20) NOT NULL DEFAULT '0';

CREATE TABLE equipment_variable (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER NOT NULL,
    name VARCHAR(20) NOT NULL,
    db_address VARCHAR(20) NOT NULL,
    offset_byte INTEGER NOT NULL,
    offset_bit INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (equipment_id) REFERENCES counting_equipment(id)
);

INSERT INTO audit_script (run_date, process, version, schema)
VALUES
    (CURRENT_DATE, '0002_equipmentVariablesPLCipDBaddress.sql', '1.0.0', '1.0.0_0002');