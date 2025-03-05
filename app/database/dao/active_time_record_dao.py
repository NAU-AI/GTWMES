from database.connection.db_connection import SessionLocal
from model.variable import Variable
from model.active_time_record import ActiveTimeRecord


class ActiveTimeRecordDAO:
    def __init__(self):
        self.session = SessionLocal()

    def find_by_id(self, active_time_id: int) -> ActiveTimeRecord:
        return (
            self.session.query(ActiveTimeRecord)
            .filter(ActiveTimeRecord.id == active_time_id)
            .first()
        )

    def find_by_variable_id(self, variable_id: int) -> list[ActiveTimeRecord]:
        return (
            self.session.query(ActiveTimeRecord)
            .filter(ActiveTimeRecord.variable_id == variable_id)
            .all()
        )

    def find_by_equipment_id(self, equipment_id: int) -> list[ActiveTimeRecord]:
        return (
            self.session.query(ActiveTimeRecord)
            .join(Variable)
            .filter(Variable.equipment_id == equipment_id)
            .all()
        )

    def find_all(self) -> list[ActiveTimeRecord]:
        return self.session.query(ActiveTimeRecord).all()

    def save(self, active_time_record: ActiveTimeRecord) -> ActiveTimeRecord:
        self.session.add(active_time_record)
        self.session.commit()
        self.session.refresh(active_time_record)
        return active_time_record

    def delete(self, active_time_id: int) -> bool:
        active_time_record = (
            self.session.query(ActiveTimeRecord)
            .filter(ActiveTimeRecord.id == active_time_id)
            .first()
        )
        if not active_time_record:
            return False

        self.session.delete(active_time_record)
        self.session.commit()
        return True

    def find_latest_by_equipment_id(self, equipment_id: int) -> ActiveTimeRecord:
        return (
            self.session.query(ActiveTimeRecord)
            .join(Variable, ActiveTimeRecord.variable_id == Variable.id)
            .filter(Variable.equipment_id == equipment_id)
            .order_by(ActiveTimeRecord.registered_at.desc())
            .first()
        )

    def close(self):
        self.session.close()
