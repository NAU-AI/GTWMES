from dao.counter_record_dao import CounterRecordDAO
from model import CounterRecord
from app.exception import NotFoundException, ServiceException
from app.utility.logger import Logger

logger = Logger.get_logger(__name__)


class CounterRecordService:
    def __init__(self, counter_record_dao: CounterRecordDAO = None):
        self.counter_record_dao = counter_record_dao or CounterRecordDAO()

    def create_counter_record(self, counter_record: CounterRecord) -> CounterRecord:
        try:
            saved_record = self.counter_record_dao.save(counter_record)
            logger.info(
                f"Created counter record for output ID {counter_record.equipment_output_id} with value {counter_record.real_value}"
            )
            return saved_record
        except Exception as e:
            logger.error(f"Error creating counter record: {e}", exc_info=True)
            raise ServiceException("Unable to create counter record.") from e

    def get_by_output_id(self, output_id: int) -> list[CounterRecord]:
        try:
            return self.counter_record_dao.find_by_output_id(output_id)
        except Exception as e:
            logger.error(
                f"Error fetching counter records for output ID '{output_id}': {e}",
                exc_info=True,
            )
            raise ServiceException("Unable to fetch counter records.") from e

    def delete_counter_record(self, record_id: int) -> dict:
        try:
            deleted = self.counter_record_dao.delete(record_id)
            if not deleted:
                raise NotFoundException(
                    f"Counter record with ID '{record_id}' not found"
                )

            logger.info(f"Deleted counter record with ID {record_id}")
            return {
                "message": f"Counter record with ID {record_id} deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting counter record: {e}", exc_info=True)
            raise ServiceException("Unable to delete counter record.") from e
