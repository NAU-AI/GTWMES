from database.connection.db_connection import SessionLocal
from model import CounterRecord


class CounterRecordDAO:
    def __init__(self):
        self.session = SessionLocal()

    def find_by_id(self, counter_id: int) -> CounterRecord:
        return (
            self.session.query(CounterRecord)
            .filter(CounterRecord.id == counter_id)
            .first()
        )

    def find_by_equipment_output_id(
        self, equipment_output_id: int
    ) -> list[CounterRecord]:
        return (
            self.session.query(CounterRecord)
            .filter(CounterRecord.equipment_output_id == equipment_output_id)
            .all()
        )

    def find_last_by_equipment_output_id(
        self, equipment_output_id: int
    ) -> CounterRecord:
        return (
            self.session.query(CounterRecord)
            .filter(CounterRecord.equipment_output_id == equipment_output_id)
            .order_by(CounterRecord.registered_at.desc())
            .first()
        )

    def find_all(self) -> list[CounterRecord]:
        return self.session.query(CounterRecord).all()

    def save(self, counter_record: CounterRecord) -> CounterRecord:
        self.session.add(counter_record)
        self.session.commit()
        self.session.refresh(counter_record)
        return counter_record

    def update(self, counter_id: int, updated_data: dict) -> CounterRecord:
        counter_record = (
            self.session.query(CounterRecord)
            .filter(CounterRecord.id == counter_id)
            .first()
        )
        if not counter_record:
            return None

        for key, value in updated_data.items():
            setattr(counter_record, key, value)

        self.session.commit()
        self.session.refresh(counter_record)
        return counter_record

    def delete(self, counter_id: int) -> bool:
        counter_record = (
            self.session.query(CounterRecord)
            .filter(CounterRecord.id == counter_id)
            .first()
        )
        if not counter_record:
            return False

        self.session.delete(counter_record)
        self.session.commit()
        return True

    def close(self):
        self.session.close()
