from asyncio.log import logger
from database.dao.equipment_variables_dao import EquipmentVariablesDAO
from exception.Exception import ServiceException


class EquipmentVariablesService:
    def __init__(self, equipment_variables_dao=None):
        self.equipment_variables_dao = equipment_variables_dao or EquipmentVariablesDAO()

    def get_equipment_variables(self, equipment_id, return_all=True):
        if not equipment_id:
            raise ValueError("equipment_id is required")

        try:
            equipment_variables = self.equipment_variables_dao.get_equipment_variables_by_equipment_id(equipment_id)
            if not equipment_variables:
                return None
            alarms_address = self._get_equipment_variable_by_label(equipment_variables, 'alarm_', allow_multiple=True)
            outputs_address = self._get_equipment_variable_by_label(equipment_variables, 'output_', allow_multiple=True)
            active_time_address = self._get_equipment_variable_by_label(equipment_variables, 'activeTime')
            equipment_status_address = self._get_equipment_variable_by_label(equipment_variables, 'equipmentStatus')
            is_equipment_enabled_address = self._get_equipment_variable_by_label(equipment_variables, 'isEquipmentEnabled')
            target_amount_address = self._get_equipment_variable_by_label(equipment_variables, 'targetAmount')
            matched_names = [
                    active_time_address['name'],
                    equipment_status_address['name'],
                    is_equipment_enabled_address['name'],
                    target_amount_address['name'],
                ]
            matched_prefixes = ['alarm_', 'output_']
            unmatched = self._get_unmatched_equipment_variables(
                equipment_variables,
                matched_names,
                matched_prefixes,
            )
            if return_all:
                return {
                        "alarms": alarms_address,
                        "outputs": outputs_address,
                        "active_time": active_time_address,
                        "equipment_status": equipment_status_address,
                        "is_equipment_enabled": is_equipment_enabled_address,
                        "target_amount": target_amount_address,
                        "unmatched": unmatched,
                        }
            else:
                return is_equipment_enabled_address, target_amount_address

        except Exception as e:
            logger.error(
                f"Service error while fetching equipment variables for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException("An error occurred while fetching the equipment variables")

    def _get_equipment_variable_by_label(self, equipment_variables, label, allow_multiple=False):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            if allow_multiple:
                return [item for item in equipment_variables if item['name'].startswith(label)]
            else:
                return next(item for item in equipment_variables if item['name'] == label)
        except StopIteration:
            logger.error(f"Item with name '{label}' not found in equipment_variables.")
            return None 
        except Exception as e:
            logger.error(f"Service error while getting {label} from equipment_variables: {e}")
            raise ServiceException(f"An error occurred while getting {label} from the equipment variables")
        
    def _get_unmatched_equipment_variables(self, equipment_variables, matched_names=None, matched_prefixes=None):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        if matched_names is None:
            matched_names = []
        if matched_prefixes is None:
            matched_prefixes = []

        try:
            unmatched = []
            
            for idx, item in enumerate(equipment_variables):
                logger.debug(f"Item at index {idx} has type {type(item)}")
                
                if isinstance(item, dict):
                    item_name = item.get('name', None)
                elif hasattr(item, 'name'):
                    item_name = getattr(item, 'name', None)
                else:
                    logger.debug(f"Item at index {idx} does not have a 'name' attribute: {item}")
                    item_name = None
                
                if item_name and item_name not in matched_names and not any(item_name.startswith(prefix) for prefix in matched_prefixes):
                    unmatched.append(item_name)

            return unmatched
        
        except Exception as e:
            logger.error(
                f"Service error while getting unmatched equipment variables: {e}, input: {equipment_variables}"
            )
            raise ServiceException("An error occurred while getting unmatched equipment variables")