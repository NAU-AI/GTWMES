--example
--ALTER TABLE 
--ADD COLUMN  ;

INSERT INTO audit_script (run_date, process, version, schema)
VALUES
    (CURRENT_DATE, '0001_example', '1.0.0', '1.0.0_0001');