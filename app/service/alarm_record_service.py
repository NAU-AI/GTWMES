from dao.alarm_record_dao import AlarmRecordDAO
from model import AlarmRecord
from app.exception import NotFoundException, ServiceException
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class AlarmRecordService:
    def __init__(self, alarm_record_dao: AlarmRecordDAO = None):
        self.alarm_record_dao = alarm_record_dao or AlarmRecordDAO()

    def create_alarm_record(self, alarm_record: AlarmRecord) -> AlarmRecord:
        try:
            saved_alarm = self.alarm_record_dao.save(alarm_record)
            logger.info(
                f"Created alarm record with ID {saved_alarm.id} and value {saved_alarm.value}"
            )
            return saved_alarm
        except Exception as e:
            logger.error(f"Error creating alarm record: {e}", exc_info=True)
            raise ServiceException("Unable to create alarm record.") from e

    def get_alarm_record_by_id(self, alarm_id: int) -> AlarmRecord:
        try:
            alarm_record = self.alarm_record_dao.find_by_id(alarm_id)
            if not alarm_record:
                raise NotFoundException(f"Alarm record with ID '{alarm_id}' not found")
            return alarm_record
        except Exception as e:
            logger.error(
                f"Error fetching alarm record by ID '{alarm_id}': {e}", exc_info=True
            )
            raise ServiceException("Unable to fetch alarm record.") from e

    def get_by_equipment_id(self, equipment_id: int) -> list[AlarmRecord]:
        try:
            return self.alarm_record_dao.find_by_equipment_id(equipment_id)
        except Exception as e:
            logger.error(
                f"Error fetching alarm records for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch alarm records.") from e

    def get_all_alarm_records(self) -> list[AlarmRecord]:
        try:
            return self.alarm_record_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all alarm records.", exc_info=True)
            raise ServiceException("Unable to fetch all alarm records.") from e

    def get_by_variable_id(self, variable_id: int) -> list[AlarmRecord]:
        try:
            alarms = self.alarm_record_dao.find_by_variable_id(variable_id)
            if not alarms:
                raise NotFoundException(
                    f"No alarms found for variable ID '{variable_id}'"
                )

            return alarms
        except Exception as e:
            logger.error(
                f"Error fetching alarms for variable ID '{variable_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch alarm records.") from e

    def update_alarm_record(self, alarm_id: int, new_value: int) -> AlarmRecord:
        try:
            existing_alarm = self.alarm_record_dao.find_by_id(alarm_id)
            if not existing_alarm:
                raise NotFoundException(f"Alarm record with ID '{alarm_id}' not found")

            existing_alarm.value = new_value
            self.alarm_record_dao.save(existing_alarm)

            logger.info(f"Updated alarm record ID {alarm_id} to new value {new_value}")
            return existing_alarm
        except Exception as e:
            logger.error(f"Error updating alarm record: {e}", exc_info=True)
            raise ServiceException("Unable to update alarm record.") from e

    def delete_alarm_record(self, alarm_id: int) -> dict:
        try:
            deleted = self.alarm_record_dao.delete(alarm_id)
            if not deleted:
                raise NotFoundException(f"Alarm record with ID '{alarm_id}' not found")

            logger.info(f"Deleted alarm record with ID {alarm_id}")
            return {"message": f"Alarm record with ID {alarm_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting alarm record: {e}", exc_info=True)
            raise ServiceException("Unable to delete alarm record.") from e

    def insert_alarm_by_equipment_id(
        self, equipment_id: int, value: int
    ) -> AlarmRecord:
        try:
            new_alarm = self.alarm_record_dao.insert_alarm_by_equipment_id(
                equipment_id, value
            )
            if not new_alarm:
                raise NotFoundException(
                    f"No variable found for equipment ID '{equipment_id}', unable to create alarm."
                )

            logger.info(
                f"Inserted alarm for equipment ID {equipment_id} with value {value}"
            )
            return new_alarm
        except Exception as e:
            logger.error(
                f"Error inserting alarm by equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to insert alarm.") from e

    def delete_counter_record(self, record_id: int) -> bool:
        try:
            deleted = self.counter_record_dao.delete(record_id)
            if not deleted:
                raise NotFoundException(
                    f"Counter record with ID '{record_id}' not found"
                )

            logger.info(f"Deleted counter record with ID {record_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting counter record: {e}", exc_info=True)
            raise ServiceException("Unable to delete counter record.") from e
