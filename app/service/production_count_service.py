from service.production_order_service import ProductionOrderService
from service.equipment_service import EquipmentService
from service.equipment_output_service import EquipmentOutputService
from service.active_time_record_service import ActiveTimeRecordService
from service.alarm_record_service import AlarmRecordService
from service.counter_record_service import CounterRecordService
from service.plc_service import PlcService
from model.equipment import Equipment
from exception.Exception import ServiceException, NotFoundException
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class ProductionCountService:
    def __init__(
        self,
        production_order_service: ProductionOrderService = None,
        equipment_service: EquipmentService = None,
        equipment_output_service: EquipmentOutputService = None,
        active_time_service: ActiveTimeRecordService = None,
        alarm_service: AlarmRecordService = None,
        counter_record_service: CounterRecordService = None,
        plc_service: PlcService = None,
    ):
        self.production_order_service = (
            production_order_service or ProductionOrderService()
        )
        self.equipment_service = equipment_service or EquipmentService()
        self.equipment_output_service = (
            equipment_output_service or EquipmentOutputService()
        )
        self.active_time_service = active_time_service or ActiveTimeRecordService()
        self.alarm_service = alarm_service or AlarmRecordService()
        self.counter_record_service = counter_record_service or CounterRecordService()
        self.plc_service = plc_service or PlcService()

    def build_production_count(self, equipment_code: str, message_type: str) -> dict:
        try:
            logger.info(
                f"Building production count message for equipment '{equipment_code}'"
            )

            equipment = self._get_equipment(equipment_code)
            if not equipment:
                raise NotFoundException(
                    f"Equipment with code '{equipment_code}' not found"
                )

            production_order_code = self._get_active_production_order_code(equipment)
            active_time = self.active_time_service.get_active_record_time(equipment.id)
            alarms = self.alarm_service.get_by_equipment_id(equipment.id)
            counters = self._get_counters(equipment.id)

            equipment_status = self._get_equipment_status(equipment)

            return self._prepare_message(
                json_type=message_type,
                equipment_code=equipment.code,
                production_order_code=production_order_code,
                equipment_status=equipment_status,
                active_time=active_time,
                alarms=alarms,
                counters=counters,
            )

        except Exception as e:
            logger.error(f"Error building production count message: {e}", exc_info=True)
            raise ServiceException("Failed to build production count message.") from e

    def _get_equipment(self, equipment_code: str) -> Equipment:
        try:
            return self.equipment_service.get_equipment_by_code(equipment_code)
        except Exception as e:
            logger.error(
                f"Error fetching equipment '{equipment_code}': {e}", exc_info=True
            )
            return None

    def _get_active_production_order_code(self, equipment: Equipment) -> str:
        production_order = self.production_order_service.get_production_order_by_equipment_id_and_status(
            equipment.id, is_completed=False
        )
        return production_order.code if production_order else ""

    def _get_counters(self, equipment_id: int) -> list:
        try:
            outputs = self.equipment_output_service.get_by_equipment_id(equipment_id)
            counter_records = []

            for output in outputs:
                counter_value = (
                    self.counter_record_service.get_last_by_equipment_output_id(
                        output.id
                    )
                )
                counter_records.append(
                    {
                        "outputCode": output.code,
                        "value": counter_value,
                    }
                )

            return counter_records

        except Exception as e:
            logger.error(
                f"Error fetching counters for equipment ID {equipment_id}: {e}",
                exc_info=True,
            )
            return []  # Return an empty list if there's an error

    def _get_equipment_status(self, equipment: Equipment) -> int:
        try:
            return self.plc_service.read_equipment_status(equipment.id)
        except Exception:
            logger.warning(
                f"Could not fetch equipment status for '{equipment.code}', defaulting to 0"
            )
            return 0

    def _prepare_message(self, **kwargs) -> dict:
        return {
            "jsonType": kwargs.get("json_type", ""),
            "equipmentCode": kwargs.get("equipment_code", ""),
            "productionOrderCode": kwargs.get("production_order_code", ""),
            "equipmentStatus": kwargs.get("equipment_status", 0),
            "activeTime": kwargs.get("active_time", 0),
            "alarms": kwargs.get("alarms", []),
            "counters": kwargs.get("counters", []),
        }
