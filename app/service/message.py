import json

#I will need to change this functions in order to know all the equipment_variables that each equipment have
#then It will be necessary send the message with all the parameters.
#But 1st we have to decide the better way to send it on our protocol

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
            
            active_time_value = active_time_dao.getLastActiveTimeByEquipmentId(equipment_found['id'])

            time = 0
            if(active_time_value != None):
                time = active_time_value['active_time']
            
            counters = []
            for output in outputs:
                outputTotal = counter_record_dao.getLastCounterRecordByEquipmentOutputId(output['id'])
                if(outputTotal == None):
                    outputTotal = 0
                else:
                    outputTotal = outputTotal["real_value"]
                counters.append({"outputCode": output['code'], "value": outputTotal})

            if "productionOrderCode" in data:
                productionOrderCode = data["productionOrderCode"]
            else:
                productionOrderCode = ""

            alarms = alarm_dao.getAlarmsByEquipmentId(equipment_found['id'])
            if alarms != None:
                alarm = [alarms['alarm_0'], alarms['alarm_1'], alarms['alarm_2'], alarms['alarm_3']]
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
        #totalActiveTimeEquipment = active_time_dao.getActiveTimeTotalValueByEquipmentId(data['equipment_id'])
        active_time_value = active_time_dao.getLastActiveTimeByEquipmentId(data['equipment_id'])

        time = 0
        if(active_time_value != None):
            #time = totalActiveTimeEquipment["totalactivevalue"]
            time = active_time_value['active_time']

        counters = []
        for output in outputs:
            outputTotal = counter_record_dao.getLastCounterRecordByEquipmentOutputId(output['id'])
            if(outputTotal == None):
                outputTotal = 0
            else:
                outputTotal = outputTotal["real_value"]
            counters.append({"outputCode": output['code'], "value": outputTotal})


        alarms = alarm_dao.getAlarmsByEquipmentId(data['equipment_id'])
        if alarms != None:
            alarm = [alarms['alarm_0'], alarms['alarm_1'], alarms['alarm_2'], alarms['alarm_3']]
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