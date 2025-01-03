BEGIN;

ALTER TABLE production_order
RENAME COLUMN finished TO is_completed;

ALTER TABLE production_order ALTER COLUMN is_completed DROP DEFAULT;

UPDATE production_order
SET is_completed = CASE 
    WHEN is_completed = 1 THEN 1
    WHEN is_completed = 0 THEN 0
    ELSE NULL
END;

ALTER TABLE production_order
ALTER COLUMN is_completed TYPE BOOLEAN USING (is_completed = 1);

ALTER TABLE production_order ALTER COLUMN is_completed SET DEFAULT FALSE;

INSERT INTO audit_script (run_date, process, version, schema)
VALUES
    (CURRENT_DATE, '0002_finishedToIsCompleted.sql', '1.0.0', '1.0.0_0002');

COMMIT;
