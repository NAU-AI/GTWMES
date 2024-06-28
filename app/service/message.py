import json
from random import randint

class MessageService:
    def __init__(self, configuration_dao, active_time_dao, counter_record_dao):
        self.configuration_dao = configuration_dao
        self.active_time_dao = active_time_dao
        self.counter_record_dao = counter_record_dao

    def sendResponseMessage(self, client, topicSend, data, jsonType): 
        configuration_dao = self.configuration_dao
        active_time_dao = self.active_time_dao
        counter_record_dao = self.counter_record_dao

        equipment_found = configuration_dao.getCountingEquipmentByCode(data)  
        outputs = configuration_dao.getEquipmentOutputByEquipmentId(equipment_found['code'])
        totalActiveTimeEquipment = active_time_dao.getActiveTimeTotalValueByEquipmentId(equipment_found['id'])
        
        time = 0
        if(totalActiveTimeEquipment != None):
            time = totalActiveTimeEquipment["totalactivevalue"]
            
        counters = []
        for output in outputs:
            outputTotal = counter_record_dao.getCounterRecordTotalValueByEquipmentOutputId(output['id'])
            if(outputTotal == None):
                outputTotal = 0
            else:
                outputTotal = outputTotal["totalvalue"]
            counters.append({"outputCode": output['code'], "value": outputTotal})

        if "productionOrderCode" in data:
            productionOrderCode = data["productionOrderCode"]
        else:
            productionOrderCode = ""

        alarm = [0, 0, 0, 0]

        message = {}

        message.update({"jsonType": jsonType})
        message.update({"equipmentCode": equipment_found['code']})
        message.update({"productionOrderCode": productionOrderCode})
        message.update({"equipmentStatus": equipment_found['equipment_status']})
        message.update({"activeTime":time})
        message.update({"alarms":alarm})
        message.update({"counters": counters})

        client.publish(topicSend, json.dumps(message), qos=1)
        print("Response message sent")



    def sendProductionCount(self, client, topicSend, data): 
        configuration_dao = self.configuration_dao
        active_time_dao = self.active_time_dao
        counter_record_dao = self.counter_record_dao

        outputs = configuration_dao.getEquipmentOutputByEquipmentId(data['equipment_code'])
        totalActiveTimeEquipment = active_time_dao.getActiveTimeTotalValueByEquipmentId(data['equipment_id'])

        time = 0
        if(totalActiveTimeEquipment != None):
            time = totalActiveTimeEquipment["totalactivevalue"]

        counters = []
        for output in outputs:
            outputTotal = counter_record_dao.getCounterRecordTotalValueByEquipmentOutputId(output['id'])
            if(outputTotal == None):
                outputTotal = 0
            else:
                outputTotal = outputTotal["totalvalue"]
            counters.append({"outputCode": output['code'], "value": outputTotal})


        alarm = [0, 0, 0, 0]

        message = {
        "jsonType": "ProductionCount",
        "equipmentCode": data['equipment_code'], 
        "productionOrderCode": data['code'],
        "equipmentStatus": data['equipment_status'],
        "activeTime":time,
        "alarms": alarm,
        "counters": counters
        }
        message.update({"jsonType": "ProductionCount"})
        message.update({"equipmentCode": data['equipment_code']})
        message.update({"productionOrderCode": data['code']})
        message.update({"equipmentStatus": data['equipment_status']})
        message.update({"activeTime":time})
        message.update({"alarms":alarm})
        message.update({"counters": counters})

        client.publish(topicSend, json.dumps(message), qos=1)
        print("ProductionCount sent")