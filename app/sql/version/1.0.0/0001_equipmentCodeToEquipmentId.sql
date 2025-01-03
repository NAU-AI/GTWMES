BEGIN;

ALTER TABLE equipment_output
RENAME COLUMN equipment_code TO equipment_id;

ALTER TABLE equipment_output
ALTER COLUMN equipment_id TYPE INTEGER USING (equipment_id::integer);

ALTER TABLE equipment_output
ADD FOREIGN KEY (equipment_id) REFERENCES counting_equipment(id);

INSERT INTO audit_script (run_date, process, version, schema)
VALUES
    (CURRENT_DATE, '0001_equipmentCodeToEquipmentId.sql', '1.0.0', '1.0.0_0001');

COMMIT;