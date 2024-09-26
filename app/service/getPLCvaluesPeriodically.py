import os
import random
import sys
import time
import snap7

from database.dao.activeTime import ActiveTimeDAO
from database.dao.alarm import AlarmDAO
from database.dao.equipmentVariables import EquipmentVariablesDAO
from database.dao.counterRecord import CounterRecordDAO
from database.dao.configuration import ConfigurationDAO
from service.PLC.snap7 import plc_connect, plc_disconnect, read_int 
import database.connectDB
from database.config import load_config

def getPLCvaluesPeriodically():
    config = load_config()
    conn = database.connectDB.connect(config)

    active_time_dao = ActiveTimeDAO(conn)
    alarms_dao = AlarmDAO(conn)
    configuration_dao = ConfigurationDAO(conn)
    counter_record_dao = CounterRecordDAO(conn)
    equipment_variables_dao = EquipmentVariablesDAO(conn)


    duration = 1
    while True:

        equipments = configuration_dao.getCountingEquipmentAll()

        for equipment in equipments:
            if equipment['plc_ip'] is not None and equipment['plc_ip'] != '0':
                equipment_variables = equipment_variables_dao.getEquipmentVariablesByEquipmentId(equipment['id'])
                array_of_equipment_variables_values = []
                # Connect to the PLC
                plc = plc_connect()

                if plc is not None:    
                    for equipment_var in equipment_variables:
                        equipment_var_value = read_int(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']))
                        array_of_equipment_variables_values.append(
                            {
                            "name": equipment_var['name'],
                            "value": equipment_var_value
                            }
                        )
                        
                plc_disconnect(plc)

                alarms = {item['name']: item['value'] for item in array_of_equipment_variables_values if 'alarm' in item['name']}
                outputs = [item for item in array_of_equipment_variables_values if 'output' in item['name']]
                non_alarms = [item for item in array_of_equipment_variables_values if 'alarm' not in item['name']]
                non_alarms_and_non_outputs = [item for item in non_alarms if 'output' not in item['name']]

                equipment_db_outputs = configuration_dao.getEquipmentOutputById(equipment['id'])

                #add counter records
                for index, output in enumerate(equipment_db_outputs):
                    if index < len(outputs):
                        output_actual_value = counter_record_dao.getCounterRecordTotalValueByEquipmentOutputId(output["id"])
                        if outputs[index]['value']-output_actual_value['totalvalue'] > 0:
                            counter_record_dao.insertCounterRecord(output["id"], outputs[index]['value']-output_actual_value['totalvalue'])

                #add/update alarms
                alarms_from_this_equipment = alarms_dao.getAlarmsByEquipmentId(equipment['id'])
                if alarms_from_this_equipment is None:
                    alarms_dao.insertAlarm(equipment['id'], alarms)
                else: 
                    alarms_dao.updateAlarmByEquipmentId(equipment['id'], alarms)

                
                #add active_time
                active_time_from_equipment = active_time_dao.getActiveTimeTotalValueByEquipmentId(equipment['id'])
                active_time_value = 0

                for item in non_alarms_and_non_outputs:
                    if item['name'] == 'activeTime':
                        active_time_value = item['value']
                        break  

                if active_time_value - active_time_from_equipment['totalactivevalue'] > 0:
                    active_time_dao.insertActiveTime(equipment['id'], active_time_value - active_time_from_equipment['totalactivevalue'])

                #set equipmentStatus
                for item in non_alarms_and_non_outputs:
                    if item['name'] == 'equipmentStatus':
                        equipment_status_value = item['value']
                        break  
                configuration_dao.updateCountingEquipmentStatus(equipment['id'], equipment_status_value)
           

        time.sleep(duration)
