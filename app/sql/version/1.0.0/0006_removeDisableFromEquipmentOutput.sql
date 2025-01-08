DO $$
BEGIN

    EXECUTE 'ALTER TABLE equipment_output DROP COLUMN disable';

    INSERT INTO audit_script (run_date, process, version, schema)
    VALUES
        (CURRENT_DATE, '0006_removeDisableFromEquipmentOutput.sql', '1.0.0', '1.0.0_0006');
END $$;