class ProductionOrderService:
    def __init__(self, configuration_dao, production_order_dao, active_time_dao):
        self.configuration_dao = configuration_dao
        self.production_order_dao = production_order_dao
        self.active_time_dao = active_time_dao

    def productionOrderInit(self, data):

        configuration_dao = self.configuration_dao
        production_order_dao = self.production_order_dao

        #check if exists some counting_equipment with this code and get this id
        equipment_data = configuration_dao.getCountingEquipmentByCode(data)

        already_exist_this_production_order = production_order_dao.getProductionOrderByCodeAndCEquipmentId(equipment_data['id'], data)

        active_time_dao = self.active_time_dao
        
        if already_exist_this_production_order == None:
            #create new production order
            production_order_dao.insertProductionOrder(equipment_data['id'], data)

            production_order_dao.setEquipmentStatus(equipment_data['id'], 0)

            already_exist_this_equipmentId_at_active_time = active_time_dao.getActiveTimeByEquipmentId(equipment_data['id'])

            if already_exist_this_equipmentId_at_active_time != None:
                #if exists, set equipment active time to zero
                active_time_dao.setActiveTime(equipment_data['id'], 0)
            else:
                #if not, create active time for this equipment 
                active_time_dao.insertActiveTime(equipment_data['id'], 0)
    
        print("ProductionInit function done")

    def productionOrderConclusion(self, data):
        configuration_dao = self.configuration_dao
        production_order_dao = self.production_order_dao

        #check if exists some counting_equipment with this code and get this id
        equipment_data = configuration_dao.getCountingEquipmentByCode(data)

        #setting po as finished
        production_order_dao.setPOFinished(equipment_data['id'])

        #setting equipment status using isEquipmentEnabled property from MQTT message
        production_order_dao.setEquipmentStatus(equipment_data['id'], 0)

        #setting equipment active time to zero
        active_time_dao = self.active_time_dao
        active_time_dao.setActiveTime(equipment_data['id'], 0)

        print("ProductionConclusion function done")
        