from asyncio.log import logger
from exception.Exception import DatabaseException
from database.dao.counter_record_dao import CounterRecordDAO


class CounterRecordService:
    def __init__(self, counter_record_dao=None):
        self.counter_record_dao = counter_record_dao or CounterRecordDAO()

    def build_counters(self, outputs):
        if not outputs or not isinstance(outputs, list):
            raise ValueError("outputs must be a non-empty list")

        counters = []
        for output in outputs:
            if not hasattr(output, "id") or not hasattr(output, "code"):
                raise ValueError("Each output must have 'id' and 'code' attributes")

            try:
                counter_record = self.counter_record_dao.get_last_counter_record_by_equipment_output_id(
                    output.id
                )
                counters.append(
                    {
                        "outputCode": output.code,
                        "alias": counter_record.alias if counter_record else None,
                        "value": counter_record.real_value if counter_record else 0,
                    }
                )
            except DatabaseException as e:
                logger.error(
                    f"Failed to build counter for output {output.id}: {e}",
                    exc_info=True,
                )
                counters.append(
                    {
                        "outputCode": output.code,
                        "alias": None,
                        "value": 0,
                        "error": "Failed to fetch counter record",
                    }
                )

        return counters
