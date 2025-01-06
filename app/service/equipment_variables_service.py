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
                return {
                    "message": f"No equipment variables found for equipment_id {equipment_id}",
                    "equipment_variables": None,
                }
            alarms = self._get_alarms_equipment_variable(equipment_variables)
            outputs = self._get_outputs_equipment_variable(equipment_variables)
            active_time = self._get_active_time_equipment_variable(equipment_variables)
            equipment_status = self._get_equipment_status_equipment_variable(equipment_variables)
            is_equipment_enabled = self._get_is_equipment_enabled_equipment_variable(equipment_variables)
            target_amount = self._get_target_amount_equipment_variable(equipment_variables)
            matched_names = [
                    active_time['name'],
                    equipment_status['name'],
                    is_equipment_enabled['name'],
                    target_amount['name'],
                ]
            matched_prefixes = ['alarm_', 'output_']
            unmatched = self._get_unmatched_equipment_variables(
                equipment_variables,
                matched_names,
                matched_prefixes,
            )
            if return_all:
                return alarms, outputs, active_time, equipment_status, is_equipment_enabled, target_amount, unmatched
            else:
                return is_equipment_enabled, target_amount

        except Exception as e:
            logger.error(
                f"Service error while fetching equipment variables for equipment_id {equipment_id}: {e}"
            )
            raise ServiceException("An error occurred while fetching the equipment variables")
        
    def _get_alarms_equipment_variable(self, equipment_variables):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            return [item for item in equipment_variables if item['name'].startswith('alarm_')]
        except Exception as e:
            logger.error(
                f"Service error while getting alarms from equipment_variables: {e}"
            )
            raise ServiceException("An error occurred while getting alarms from the equipment variables")
    
    def _get_outputs_equipment_variable(self, equipment_variables):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            return [item for item in equipment_variables if item['name'].startswith('output_')]
        except Exception as e:
            logger.error(
                f"Service error while getting outputs from equipment_variables: {e}"
            )
            raise ServiceException("An error occurred while getting outputs from the equipment variables")
    
    def _get_active_time_equipment_variable(self, equipment_variables):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            return next(item for item in equipment_variables if item['name'] == 'activeTime')
        except Exception as e:
            logger.error(
                f"Service error while getting active_time from equipment_variables: {e}"
            )
            raise ServiceException("An error occurred while getting active_time from the equipment variables")
    
    def _get_equipment_status_equipment_variable(self, equipment_variables):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            return next(item for item in equipment_variables if item['name'] == 'equipmentStatus')
        except Exception as e:
            logger.error(
                f"Service error while getting equipment_status from equipment_variables: {e}"
            )
            raise ServiceException("An error occurred while getting equipment_status from the equipment variables")
    
    def _get_is_equipment_enabled_equipment_variable(self, equipment_variables):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            return next(item for item in equipment_variables if item['name'] == 'isEquipmentEnabled')
        except Exception as e:
            logger.error(
                f"Service error while getting is_equipment_enabled from equipment_variables: {e}"
            )
            raise ServiceException("An error occurred while getting is_equipment_enabled from the equipment variables")

    def _get_target_amount_equipment_variable(self, equipment_variables):
        if not equipment_variables:
            raise ValueError("equipment_variables is required")

        try:
            return next(item for item in equipment_variables if item['name'] == 'targetAmount')
        except Exception as e:
            logger.error(
                f"Service error while getting target_amount from equipment_variables: {e}"
            )
            raise ServiceException("An error occurred while getting target_amount from the equipment variables")

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