import json
from random import randint

class MessageService:
    def __init__(self, configuration_dao, active_time_dao, counter_record_dao, alarm_dao):
        self.configuration_dao = configuration_dao
        self.active_time_dao = active_time_dao
        self.counter_record_dao = counter_record_dao
        self.alarm_dao = alarm_dao

    def sendResponseMessage(self, client, topicSend, data, jsonType): 
        configuration_dao = self.configuration_dao
        active_time_dao = self.active_time_dao
        counter_record_dao = self.counter_record_dao
        alarm_dao = self.alarm_dao

        equipment_found = configuration_dao.getCountingEquipmentByCode(data)  
        if equipment_found:
            outputs = configuration_dao.getEquipmentOutputByEquipmentId(equipment_found['id'])
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

            alarms = alarm_dao.getAlarmsByEquipmentId(equipment_found['id'])
            if alarms != None:
                alarm = [alarms['alarm_1'], alarms['alarm_2'], alarms['alarm_3'], alarms['alarm_4']]
            else:
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
        alarm_dao = self.alarm_dao

        outputs = configuration_dao.getEquipmentOutputByEquipmentId(data['equipment_id'])
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


        alarms = alarm_dao.getAlarmsByEquipmentId(data['equipment_id'])
        if alarms != None:
            alarm = [alarms['alarm_1'], alarms['alarm_2'], alarms['alarm_3'], alarms['alarm_4']]
        else:
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