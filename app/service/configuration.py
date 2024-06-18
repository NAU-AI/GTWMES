class ConfigurationService:
    def __init__(self, configuration_dao):
        self.configuration_dao = configuration_dao

    def createConfiguration(self, data):
        configuration_dao = self.configuration_dao

        #check if exists some counting_equipment with this code
        equipment_found = configuration_dao.getCountingEquipmentByCode(data)

        if equipment_found == None:
            #if it doesn't exists, create a new one and the outputs
            inserted_counting_equipment_id = configuration_dao.insertCountingEquipment(data)
            #like this counting equipment didn't exist, we have to insert the outputs at equipment_output
            configuration_dao.insertEquipmentOutput(inserted_counting_equipment_id, data)

        else: 
            #if exists, we update it
            updated_counting_equipment_code = configuration_dao.updateCountingEquipment(data)
            #delete existing outputs in order to add the new ones
            configuration_dao.deleteEquipmentOutput(updated_counting_equipment_code)
            #now we have to insert the outputs at equipment_output
            configuration_dao.insertEquipmentOutput(updated_counting_equipment_code, data)
        
        print("createConfiguration function done")