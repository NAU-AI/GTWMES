import logging
from database.dao.counting_equipment_dao import CountingEquipmentDAO
from database.dao.production_order_dao import ProductionOrderDAO
from service.plc_service import PlcService
from service.equipment_variables_service import EquipmentVariablesService

class ProductionOrderService:
    def __init__(self):
        self.production_order_dao = ProductionOrderDAO()
        self.counting_equipment_dao = CountingEquipmentDAO()
        self.equipment_variables_service = EquipmentVariablesService()
        self.plc_service = PlcService()

    def production_order_init(self, data):
        if not self._validate_data(data, ["productionOrderCode", "equipmentCode"]):
            logging.error("Invalid data provided for production_order_init.")
            return False

        if not data["productionOrderCode"]:
            logging.info("Production order code is empty. Skipping initialization.")
            return False

        try:
            equipment_data = self.counting_equipment_dao.get_equipment_by_code(
                data["equipmentCode"]
            )
            if not equipment_data:
                logging.warning(
                    f"Equipment with code {data['equipmentCode']} not found."
                )
                return False

            self.production_order_dao.insert_production_order(
                equipment_data.id, data["productionOrderCode"]
            )

            is_equipment_enable, target_amount = self.equipment_variables_service.get_equipment_variables(equipment_data.id, False)
            self.plc_service._get_write_function(is_equipment_enable, is_equipment_enable["type"], True)
            self.plc_service._get_write_function(target_amount, target_amount["type"], data["targetAmount"])

            logging.info(f"Production order {data['productionOrderCode']} initialized.")
            return True
        except Exception as e:
            logging.error(f"Error initializing production order: {e}")
            return False
        
    
    def production_order_conclusion(self, data):
        if not self._validate_data(data, ["equipmentCode"]):
            logging.error("Invalid data provided for production_order_conclusion.")
            return False

        try:
            equipment_data = self.counting_equipment_dao.get_equipment_by_code(
                data["equipmentCode"]
            )
            if not equipment_data:
                logging.warning(
                    f"Equipment with code {data['equipmentCode']} not found."
                )
                return False

            self.production_order_dao.update_production_order_status(
                equipment_data.id, True
            )

            is_equipment_enable, target_amount = self.equipment_variables_service.get_equipment_variables(equipment_data.id, False)
            self.plc_service._get_write_function(is_equipment_enable, is_equipment_enable["type"], False)
            self.plc_service._get_write_function(target_amount, target_amount["type"], data["targetAmount"])

            logging.info(
                f"Production order for equipment {data['equipmentCode']} updated to status {True}."
            )
            return True
        except Exception as e:
            logging.error(
                f"Error concluding production order for equipment {data['equipmentCode']}: {e}",
                exc_info=True,
            )
            return False

        
    def get_production_order_by_equipment_id_and_status(self, equipment_id, status):
        try:
            return self.production_order_dao.get_production_order_by_equipment_id_and_status(
                equipment_id, status
            )
        except Exception as e:
            logging.error(
                f"Error fetching production order for equipment {equipment_id} with status {status}: {e}",
                exc_info=True,
            )
            return None

    @staticmethod
    def _validate_data(data, required_keys):
        if not isinstance(data, dict):
            return False
        return all(key in data for key in required_keys)
        