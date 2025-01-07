from asyncio.log import logger
import logging

from service.alarm_service import AlarmService
from service.active_time_service import ActiveTimeService
from service.plc_service import PlcService
from service.counter_record_service import CounterRecordService
from service.equipment_output_service import EquipmentOutputService
from service.counting_equipment_service import CountingEquipmentService
from service.production_order_service import ProductionOrderService


class ProductionCountService:
    def __init__(
        self,
        production_order_service=None,
        counting_equipment_service=None,
        equipment_output_service=None,
        active_time_service=None,
        alarm_service=None,
        counter_record_service=None,
        plc_service=None,
    ):
        self.production_order_service = (
            production_order_service or ProductionOrderService()
        )
        self.counting_equipment_service = (
            counting_equipment_service or CountingEquipmentService()
        )
        self.equipment_output_service = (
            equipment_output_service or EquipmentOutputService()
        )
        self.counter_record_service = counter_record_service or CounterRecordService()
        self.plc_service = plc_service or PlcService()
        self.active_time_service = active_time_service or ActiveTimeService()
        self.alarm_service = alarm_service or AlarmService()

    def build_production_count(
        self, data, message_type, default_production_order_code=""
    ):
        try:
            equipment_code = data.get("code") or data.get("equipmentCode")
            equipment = self._get_equipment(
                equipment_code, equipment_id=data.get("equipment_id")
            )
            if not equipment:
                logging.warning(
                    f"No equipment found for code '{data.get('code')}' or ID '{data.get('equipment_id')}'."
                )
                return
            self.plc_service.read_plc_data(equipment.id) 
            equipment_id = equipment.id
            equipment_code = equipment.code
            equipment_status = equipment.equipment_status

            active_time = self.active_time_service.get_active_time(equipment_id)
            counters = self._get_counters(equipment_id)
            alarms = self.alarm_service.get_latest_alarm(equipment_id)
            if alarms is None:
                alarms = [0, 0, 0, 0]
            
            production_order_code = data.get("code", default_production_order_code)
            message = self._prepare_message(
                json_type=message_type,
                equipment_code=equipment_code,
                production_order_code=production_order_code,
                equipment_status=equipment_status,
                active_time=active_time,
                alarms=alarms,
                counters=counters
            )

            return message
        except Exception as e:
            logging.error(f"Error while sending message response: {e}", exc_info=True)

    def _get_counters(self, equipment_id):
        try:
            outputs = self.equipment_output_service.get_by_equipment_id(equipment_id)
            return self.counter_record_service.build_counters(outputs)
        except Exception as e:
            logging.error(
                f"Error fetching counters for equipment ID {equipment_id}: {e}",
                exc_info=True,
            )
            return []

    def _get_equipment(self, code=None, equipment_id=None):
        try:
            if equipment_id:
                return self.counting_equipment_service.get_equipment_by_id(equipment_id)
            elif code:
                return self.counting_equipment_service.get_equipment_by_code(code)
            return None
        except Exception as e:
            logger.error(
                f"Error fetching equipment with code '{code}' or ID '{equipment_id}': {e}",
                exc_info=True,
            )
            return None

    def get_all_equipment(self):
        try:
            return self.counting_equipment_service.get_all_equipment()
        except Exception as e:
            logging.error(f"Error fetching all equipment: {e}", exc_info=True)
            return []

    def should_send_message(self, elapsed_time, communication_cycle):
        return elapsed_time % communication_cycle == 0 and elapsed_time != 0

    def get_production_values(self, equipment):
        try:
            production_order = self.production_order_service.get_production_order_by_equipment_id_and_status(
                equipment.id, False
            )

            if production_order:
                payload = production_order.to_dict()
                payload.update(
                    {
                        "p_timer_communication_cycle": equipment.p_timer_communication_cycle,
                        "equipment_code": equipment.code,
                        "equipment_id": equipment.id,
                    }
                )
            else:
                payload = {
                    "code": "",
                    "equipment_code": equipment.code,
                    "equipment_id": equipment.id,
                }

            return payload
        except Exception as e:
            logging.error(
                f"Error generating production payload for equipment {equipment.id}: {e}",
                exc_info=True,
            )
            return None

    def _prepare_message(self, **kwargs):
        return {
            "jsonType": kwargs.get("json_type", ""),
            "equipmentCode": kwargs.get("equipment_code", ""),
            "productionOrderCode": kwargs.get("production_order_code", ""),
            "equipmentStatus": kwargs.get("equipment_status", 0),
            "activeTime": kwargs.get("active_time", 0),
            "alarms": kwargs.get("alarms", []),
            "counters": kwargs.get("counters", [])
        }
