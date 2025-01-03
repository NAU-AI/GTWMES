BEGIN;

ALTER TABLE equipment_output
RENAME COLUMN equipment_id TO counting_equipment_id;

INSERT INTO audit_script (run_date, process, version, schema)
VALUES
    (CURRENT_DATE, '0003_equipment_idToCounting_equipment_id.sql', '1.0.0', '1.0.0_0003');

COMMIT;