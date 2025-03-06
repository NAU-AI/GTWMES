from exception.Exception import NotFoundException
from database.connection.db_connection import SessionLocal
from model.alarm_record import AlarmRecord
from model.variable import Variable


class AlarmRecordDAO:
    def __init__(self):
        self.session = SessionLocal()

    def save(self, alarm: AlarmRecord) -> AlarmRecord:
        self.session.add(alarm)
        self.session.commit()
        self.session.refresh(alarm)
        return alarm

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

    def find_all(self) -> list[AlarmRecord]:
        return self.session.query(AlarmRecord).all()

    def find_by_variable_id(self, variable_id: int) -> list[AlarmRecord]:
        return (
            self.session.query(AlarmRecord)
            .filter(AlarmRecord.variable_id == variable_id)
            .all()
        )

    def find_by_variable_id_and_key(self, variable_id: int, key: str) -> AlarmRecord:
        return (
            self.session.query(AlarmRecord)
            .join(Variable)
            .filter(AlarmRecord.variable_id == variable_id, Variable.key == key)
            .first()
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

    def update_alarm_value_by_id(self, alarm_id: int, new_value: int) -> AlarmRecord:
        alarm = (
            self.session.query(AlarmRecord).filter(AlarmRecord.id == alarm_id).first()
        )

        if not alarm:
            raise NotFoundException(f"Alarm record with ID '{alarm_id}' not found")

        alarm.value = new_value
        self.session.commit()

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
