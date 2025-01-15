from asyncio.log import logger
from exception.Exception import DatabaseException, ServiceException
from database.dao.active_time_dao import ActiveTimeDAO


class ActiveTimeService:
    def __init__(self, active_time_dao=None):
        self.active_time_dao = active_time_dao or ActiveTimeDAO()

    def get_active_time(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id is required")

        try:
            total_active_time = self.active_time_dao.get_active_time_by_equipment_id(
                equipment_id
            )
            return total_active_time.active_time if total_active_time else 0
        except DatabaseException as e:
            logger.error(
                f"Service error while fetching active time for equipment_id {equipment_id}: {e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in get_active_time for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException(
                "An unexpected error occurred while fetching active time"
            )
        
    def insert_active_time(self, equipment_id, active_time):
        if not equipment_id or not active_time:
            raise ValueError("equipment_id and active_time are required")

        try:
            active_time_id = self.active_time_dao.insert_active_time(
                equipment_id,
                active_time
            )
            return {"message": "Active time inserted successfully", "id": active_time_id}
        except Exception as e:
            logger.error(
                f"Service error while inserting active_time for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException("An error occurred while inserting the active time")

