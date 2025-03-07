from database.connection.db_connection import SessionLocal
from model.counter_record import CounterRecord


class CounterRecordDAO:
    def save(self, counter_record: CounterRecord) -> CounterRecord:
        with SessionLocal() as session:
            session.add(counter_record)
            session.commit()
            session.refresh(counter_record)
            return counter_record

    def find_by_equipment_output_id(
        self, equipment_output_id: int
    ) -> list[CounterRecord]:
        with SessionLocal() as session:
            return (
                session.query(CounterRecord)
                .filter(CounterRecord.equipment_output_id == equipment_output_id)
                .all()
            )

    def find_last_by_equipment_output_id(
        self, equipment_output_id: int
    ) -> CounterRecord | None:
        with SessionLocal() as session:
            return (
                session.query(CounterRecord)
                .filter(CounterRecord.equipment_output_id == equipment_output_id)
                .order_by(CounterRecord.registered_at.desc())
                .first()
            )

    def delete(self, counter_id: int) -> bool:
        with SessionLocal() as session:
            counter_record = (
                session.query(CounterRecord)
                .filter(CounterRecord.id == counter_id)
                .first()
            )
            if not counter_record:
                return False

            session.delete(counter_record)
            session.commit()
            return True
