BEGIN;

ALTER TABLE counting_equipment
ADD COLUMN plc_ip VARCHAR(20) NOT NULL DEFAULT '0';

INSERT INTO audit_script (run_date, process, version, schema)
VALUES
    (CURRENT_DATE, '0005_addPLC_Ip_Column.sql', '1.0.0', '1.0.0_0005');

COMMIT;