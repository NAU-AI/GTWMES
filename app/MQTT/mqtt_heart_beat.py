import threading
import time
import datetime
from service.equipment_service import EquipmentService
from service.plc_service import PlcService
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MqttHeartbeatMonitor:
    GRACE_PERIOD = 5

    def __init__(self, plc_service=None, equipment_service=None):
        self.last_heartbeats = {}
        self.previous_cycles = {}
        self.current_alarm_status = {}

        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.monitor_thread = None

        self.plc_service = plc_service or PlcService()
        self.equipment_service = equipment_service or EquipmentService()

    def received_heartbeat(self, equipment_code):
        with self.lock:
            previous_heartbeat = self.last_heartbeats.get(equipment_code)
            self.last_heartbeats[equipment_code] = time.time()
            self.update_alarm_status(equipment_code, 0)

            previous_heartbeat_str = (
                datetime.datetime.fromtimestamp(previous_heartbeat).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if previous_heartbeat
                else "None"
            )
            new_heartbeat_str = datetime.datetime.fromtimestamp(
                self.last_heartbeats[equipment_code]
            ).strftime("%Y-%m-%d %H:%M:%S")

            logger.info(
                f"Heartbeat received for {equipment_code}. Previous: {previous_heartbeat_str}, New: {new_heartbeat_str}"
            )

    def start_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return

        logger.info("Starting heartbeat monitor thread.")

        def monitor():
            try:
                while not self.stop_event.is_set():
                    equipments = self.equipment_service.get_all_equipment_refreshed()

                    with self.lock:
                        for equipment in equipments:
                            self._process_equipment_heartbeat(equipment)

                    time.sleep(60)
            except Exception as e:
                logger.error(
                    f"Unexpected error in heartbeat monitor: {e}", exc_info=True
                )

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

        logger.info("Heartbeat monitoring started.")

    def _process_equipment_heartbeat(self, equipment):
        equipment_code = equipment.code
        current_cycle = equipment.p_timer_communication_cycle

        if equipment_code not in self.last_heartbeats:
            self.last_heartbeats[equipment_code] = time.time()
            self.current_alarm_status[equipment_code] = 0
            logger.info(f"Initialized heartbeat tracking for {equipment_code}.")
            return

        last_heartbeat = self.last_heartbeats[equipment_code]

        self._check_heartbeat_timeout(equipment_code, last_heartbeat, current_cycle)

    def _check_heartbeat_timeout(self, equipment_code, last_heartbeat, current_cycle):
        timeout = (
            3 * current_cycle * 60
        ) + self.GRACE_PERIOD  # Convert minutes to seconds
        elapsed_time = time.time() - last_heartbeat

        logger.debug(
            f"Monitoring {equipment_code}: Elapsed = {elapsed_time:.2f}s, Timeout = {timeout}s"
        )

        if elapsed_time > timeout:
            self._trigger_alarm(equipment_code, elapsed_time, timeout)

    def _trigger_alarm(self, equipment_code, elapsed_time, timeout):
        if self.current_alarm_status.get(equipment_code, 0) == 1:
            return

        logger.error(
            f"ALARM TRIGGERED: Heartbeat timeout for {equipment_code}. "
            f"Elapsed = {elapsed_time:.2f}s, Timeout = {timeout}s"
        )
        self.update_alarm_status(equipment_code, 1)

    def update_alarm_status(self, equipment_code, status):
        if self.current_alarm_status.get(equipment_code) != status:
            self.current_alarm_status[equipment_code] = status
            self._write_alarm_status(equipment_code, status)

    def _write_alarm_status(self, equipment_code, status):
        try:
            self.plc_service.write_alarm(db_address=8, byte=8, bit=0, value=status)
            logger.warning(
                f"Alarm written to PLC for {equipment_code}: Byte 8, Bit 0, Value {status}"
            )
        except Exception as e:
            logger.error(
                f"Failed to write alarm for {equipment_code}: {e}", exc_info=True
            )

    def stop_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()
            logger.info("Heartbeat monitoring stopped.")
