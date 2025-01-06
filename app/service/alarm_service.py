from asyncio.log import logger
from database.dao.alarm_dao import AlarmDAO
from exception.Exception import ServiceException


class AlarmService:
    def __init__(self, alarm_dao=None):
        self.alarm_dao = alarm_dao or AlarmDAO()

    def get_latest_alarm(self, equipment_id):
        if not equipment_id:
            raise ValueError("equipment_id is required")

        try:
            alarm = self.alarm_dao.get_alarm_by_equipment_id(equipment_id)
            if not alarm:
                return None
            return [alarm.alarm_0, alarm.alarm_1, alarm.alarm_2, alarm.alarm_3]
        except Exception as e:
            logger.error(
                f"Service error while fetching alarm for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException("An error occurred while fetching the alarm")

    def insert_alarm(self, equipment_id, alarms):
        if not equipment_id or not alarms:
            raise ValueError("equipment_id and alarms are required")

        try:
            alarm_id = self.alarm_dao.insert_alarm_by_equipment_id(equipment_id, alarms)
            return {"message": "Alarm inserted successfully", "id": alarm_id}
        except Exception as e:
            logger.error(
                f"Service error while inserting alarm for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException("An error occurred while inserting the alarm")

    def update_alarm(self, equipment_id, alarms):
        if not equipment_id or not alarms:
            raise ValueError("equipment_id and alarms are required")

        try:
            alarm_id = self.alarm_dao.update_alarm_by_equipment_id(equipment_id, alarms)
            return {"message": "Alarm updated successfully", "id": alarm_id}
        except Exception as e:
            logger.error(
                f"Service error while updating alarm for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException("An error occurred while updating the alarm")

    @staticmethod
    def _validate_alarms_data(equipment_id, alarms):
        if not equipment_id:
            raise ValueError("equipment_id is required")
        if not isinstance(alarms, dict):
            raise ValueError("alarms must be a dictionary")
        if not all(isinstance(value, bool) for value in alarms.values()):
            raise ValueError("All alarm values must be booleans")
