from database.connection.db_connection import SessionLocal
from model import AlarmRecord, Variable


class AlarmRecordDAO:
    def __init__(self):
        self.session = SessionLocal()

    def find_by_id(self, alarm_id: int) -> AlarmRecord:
        return (
            self.session.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
        )

    def find_by_equipment_id(self, equipment_id: int) -> list[AlarmRecord]:
        return (
            self.session.query(AlarmRecord)
            .join(Variable)
            .filter(Variable.equipment_id == equipment_id)
            .all()
        )

    def insert_alarm_by_equipment_id(
        self, equipment_id: int, value: int
    ) -> AlarmRecord:
        variable = (
            self.session.query(Variable)
            .filter(Variable.equipment_id == equipment_id)
            .first()
        )
        if not variable:
            return None

        new_alarm = AlarmRecord(value=value, variable_id=variable.id)
        self.session.add(new_alarm)
        self.session.commit()
        self.session.refresh(new_alarm)
        return new_alarm

    def update_alarm_by_equipment_id(self, equipment_id: int, new_value: int) -> int:
        updated_alarms = (
            self.session.query(AlarmRecord)
            .join(Variable)
            .filter(Variable.equipment_id == equipment_id)
            .update({"value": new_value})
        )

        self.session.commit()
        return updated_alarms

    def find_all(self) -> list[AlarmRecord]:
        return self.session.query(AlarmRecord).all()

    def save(self, alarm: AlarmRecord) -> AlarmRecord:
        self.session.add(alarm)
        self.session.commit()
        self.session.refresh(alarm)
        return alarm

    def update(self, alarm_id: int, updated_data: dict) -> AlarmRecord:
        alarm = (
            self.session.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
        )
        if not alarm:
            return None

        for key, value in updated_data.items():
            setattr(alarm, key, value)

        self.session.commit()
        self.session.refresh(alarm)
        return alarm

    def delete(self, alarm_id: int) -> bool:
        alarm = (
            self.session.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
        )
        if not alarm:
            return False

        self.session.delete(alarm)
        self.session.commit()
        return True

    def close(self):
        self.session.close()
