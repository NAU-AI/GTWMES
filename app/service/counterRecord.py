class CounterRecordService:
    def __init__(self, counter_record_dao):
        self.counter_record_dao = counter_record_dao

    def createCounterRecord(self, data):
        counter_record_dao = self.counter_record_dao

        counter_record_dao.insertCounterRecord(data["id"], data["value"])
            
        print("createCounterRecord function done")



    def selectCounterRecordSumById(self, data):
        counter_record_dao = self.counter_record_dao

        counter_record_dao.getCounterRecordTotalValueByEquipmentOutputId(data)
        
        print("selectCounterRecordSumById function done")