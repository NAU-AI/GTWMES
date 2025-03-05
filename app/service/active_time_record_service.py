from dao.active_time_record_dao import ActiveTimeRecordDAO
from model import ActiveTimeRecord
from app.exception import NotFoundException, ServiceException
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class ActiveTimeRecordService:
    def __init__(self, active_time_record_dao: ActiveTimeRecordDAO = None):
        self.active_time_record_dao = active_time_record_dao or ActiveTimeRecordDAO()

    def save_active_time_record(
        self, active_time_record: ActiveTimeRecord
    ) -> ActiveTimeRecord:
        try:
            saved_record = self.active_time_record_dao.save(active_time_record)
            logger.info(
                f"Created active time record with ID {saved_record.id} and active_time {saved_record.active_time}"
            )
            return saved_record
        except Exception as e:
            logger.error(f"Error creating active time record: {e}", exc_info=True)
            raise ServiceException("Unable to create active time record.") from e

    def get_active_time_record_by_id(self, active_time_id: int) -> ActiveTimeRecord:
        try:
            if record := self.active_time_record_dao.find_by_id(active_time_id):
                return record
            else:
                raise NotFoundException(
                    f"Active time record with ID '{active_time_id}' not found"
                )
        except Exception as e:
            logger.error(
                f"Error fetching active time record by ID '{active_time_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch active time record.") from e

    def get_by_variable_id(self, variable_id: int) -> list[ActiveTimeRecord]:
        try:
            return self.active_time_record_dao.find_by_variable_id(variable_id)
        except Exception as e:
            logger.error(
                f"Error fetching active time records for variable ID '{variable_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch active time records.") from e

    def get_by_equipment_id(self, equipment_id: int) -> list[ActiveTimeRecord]:
        try:
            return self.active_time_record_dao.find_by_equipment_id(equipment_id)
        except Exception as e:
            logger.error(
                f"Error fetching active time records for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch active time records.") from e

    def get_all_active_time_records(self) -> list[ActiveTimeRecord]:
        try:
            return self.active_time_record_dao.find_all()
        except Exception as e:
            logger.error("Error fetching all active time records.", exc_info=True)
            raise ServiceException("Unable to fetch all active time records.") from e

    def get_latest_by_equipment_id(self, equipment_id: int) -> ActiveTimeRecord:
        try:
            if record := self.active_time_record_dao.find_latest_by_equipment_id(
                equipment_id
            ):
                return record
            else:
                raise NotFoundException(
                    f"No active time records found for equipment ID '{equipment_id}'"
                )

        except Exception as e:
            logger.error(
                f"Error fetching latest active time record for equipment ID '{equipment_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch latest active time record.") from e

    def delete_active_time_record(self, active_time_id: int) -> bool:
        try:
            deleted = self.active_time_record_dao.delete(active_time_id)
            if not deleted:
                raise NotFoundException(
                    f"Active time record with ID '{active_time_id}' not found"
                )

            logger.info(f"Deleted active time record with ID {active_time_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting active time record: {e}", exc_info=True)
            raise ServiceException("Unable to delete active time record.") from e
