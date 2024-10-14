import snap7
from service.getPLCvalues import getPLCvalues
from service.PLC.snap7 import plc_connect, plc_disconnect, write_bool, write_int

class ProductionOrderService:
    def __init__(self, configuration_dao, production_order_dao, active_time_dao, equipment_variables_dao):
        self.configuration_dao = configuration_dao
        self.production_order_dao = production_order_dao
        self.active_time_dao = active_time_dao
        self.equipment_variables_dao = equipment_variables_dao

    def productionOrderInit(self, data):
        configuration_dao = self.configuration_dao
        production_order_dao = self.production_order_dao
        equipment_variables_dao = self.equipment_variables_dao

        if data['productionOrderCode'] != "":
            #check if exists some counting_equipment with this code and get this id
            equipment_data = configuration_dao.getCountingEquipmentByCode(data)
            getPLCvalues(equipment_data)
            
            if equipment_data['equipment_status'] == 1:
                #update production order code
                production_order_dao.updatePOcode(equipment_data['id'], data['productionOrderCode'])
            else:
                already_exist_this_production_order = production_order_dao.getProductionOrderByCodeAndCEquipmentId(equipment_data['id'], data)
            
                if already_exist_this_production_order == None:
                    #create new production order
                    production_order_dao.insertProductionOrder(equipment_data['id'], data)

                    #Here, instead of setEquipmentStatus i need to write on the PLC offset for isEquipmentEnable the value 1
                    equipment_variables = equipment_variables_dao.getEquipmentVariablesByEquipmentId(equipment_data['id'])
                    plc = plc_connect()

                    if plc is not None:    
                        for equipment_var in equipment_variables:
                            if equipment_var['name'] == "isEquipmentEnabled":
                                if data['equipmentEnabled'] is True:
                                    isEquipmentEnabled = 1
                                else:
                                    isEquipmentEnabled = 0
                                write_bool(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']), int(equipment_var['offset_bit']), isEquipmentEnabled)
                           
                            if equipment_var['name'] == "targetAmount":
                                write_int(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']), data['targetAmount'])

                    plc_disconnect(plc)

            getPLCvalues(equipment_data)

            print("ProductionInit function done")



    def productionOrderConclusion(self, data):
        configuration_dao = self.configuration_dao
        production_order_dao = self.production_order_dao
        equipment_variables_dao = self.equipment_variables_dao

        #check if exists some counting_equipment with this code and get this id
        equipment_data = configuration_dao.getCountingEquipmentByCode(data)
        #get values from PLC
        getPLCvalues(equipment_data)
        #setting po as finished
        production_order_dao.setPOFinished(equipment_data['id'])

        #setting equipment status using isEquipmentEnabled property from MQTT message
        #Here, instead of setEquipmentStatus i need to write on the PLC offset for isEquipmentEnable the value 0
        equipment_variables = equipment_variables_dao.getEquipmentVariablesByEquipmentId(equipment_data['id'])
        plc = plc_connect()

        if plc is not None:    
            for equipment_var in equipment_variables:
                if equipment_var['name'] == "isEquipmentEnabled":
                    if data['equipmentEnabled'] is True:
                        isEquipmentEnabled = 1
                    else:
                        isEquipmentEnabled = 0
                    write_bool(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']), int(equipment_var['offset_bit']), isEquipmentEnabled)
                
                if equipment_var['name'] == "targetAmount":
                    write_int(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']), data['targetAmount'])

        plc_disconnect(plc)

        getPLCvalues(equipment_data)

        print("ProductionConclusion function done")



    def productionOrderMachineInit(self, data):
        configuration_dao = self.configuration_dao
        production_order_dao = self.production_order_dao
        equipment_variables_dao = self.equipment_variables_dao

        if data['productionOrderCode'] == "" and data['equipmentStatus'] == 1:
            #check if exists some counting_equipment with this code and get this id
            equipment_data = configuration_dao.getCountingEquipmentByCode(data)

            #create new production order
            production_order_dao.insertProductionOrder(equipment_data['id'], data)


            #Here, instead of setEquipmentStatus i need to write on the PLC offset for isEquipmentEnable the value 1
            equipment_variables = equipment_variables_dao.getEquipmentVariablesByEquipmentId(equipment_data['id'])
            plc = plc_connect()

            if plc is not None:    
                for equipment_var in equipment_variables:
                    if equipment_var['name'] == "isEquipmentEnabled":
                        if data['equipmentEnabled'] is True:
                            isEquipmentEnabled = 1
                        else:
                            isEquipmentEnabled = 0
                        write_bool(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']), int(equipment_var['offset_bit']), isEquipmentEnabled)
                    
                    if equipment_var['name'] == "targetAmount":
                        write_int(plc, int(equipment_var['db_address']), int(equipment_var['offset_byte']), data['targetAmount'])

            plc_disconnect(plc)
            
            getPLCvalues(equipment_data)
        
            print("ProductionInit function done")
        