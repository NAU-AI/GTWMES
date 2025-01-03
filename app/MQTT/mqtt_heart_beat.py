import threading
import time
import logging

from database.dao.counting_equipment_dao import CountingEquipmentDAO
from service.plc_service import PlcService

class MqttHeartbeatMonitor:
    def __init__(self, plc_service=None, counting_equipment_dao=None):
        self.last_heartbeats = {}
        self.previous_cycles = {}
        self.current_alarm_status = {}

        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.monitor_thread = None

        self.plc_service = plc_service or PlcService()
        self.counting_equipment_dao = counting_equipment_dao or CountingEquipmentDAO()

    def received_heartbeat(self, equipment_code):
        with self.lock:
            self.update_alarm_status(equipment_code, 0)
            previous_heartbeat = self.last_heartbeats.get(equipment_code)
            self.last_heartbeats[equipment_code] = time.time()
            logging.info(
                f"Heartbeat received for {equipment_code}. "
                f"Previous: {previous_heartbeat}, "
                f"New: {self.last_heartbeats[equipment_code]}"
            )

    def start_monitoring(self):
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            logging.info("Starting heartbeat monitor thread.")

            def monitor():
                try:
                    GRACE_PERIOD = 5

                    while not self.stop_event.is_set():
                        equipments = self.counting_equipment_dao.get_all_equipment()
                        with self.lock:
                            for equipment in equipments:
                                equipment_code = equipment.code
                                current_cycle = equipment.p_timer_communication_cycle

                                if equipment_code not in self.last_heartbeats:
                                    self.last_heartbeats[equipment_code] = time.time()
                                    self.current_alarm_status[equipment_code] = 0
                                    logging.info(
                                        f"Initialized last_heartbeat for {equipment_code}."
                                    )
                                    continue

                                last_heartbeat = self.last_heartbeats[equipment_code]

                                self.detect_and_handle_config_changes(
                                    equipment_code, current_cycle
                                )

                                self.check_timeout_for_last_heartbeat(
                                    equipment_code,
                                    last_heartbeat,
                                    current_cycle,
                                    GRACE_PERIOD,
                                )
                        time.sleep(1)
                except Exception as e:
                    logging.error(
                        f"Unexpected error in heartbeat monitor: {e}", exc_info=True
                    )

            self.monitor_thread = threading.Thread(target=monitor, daemon=True)
            self.monitor_thread.start()
            logging.info("Heartbeat monitoring started.")

    def detect_and_handle_config_changes(self, equipment_code, current_cycle):
        if self.previous_cycles.get(equipment_code) != current_cycle:
            logging.info(
                f"Configuration updated for {equipment_code}. "
                f"New cycle = {current_cycle}s"
            )
        self.previous_cycles[equipment_code] = current_cycle

    def check_timeout_for_last_heartbeat(
        self, equipment_code, last_heartbeat, current_cycle, GRACE_PERIOD
    ):
        timeout = 3 * current_cycle + GRACE_PERIOD
        elapsed_time = time.time() - last_heartbeat
        logging.debug(
            f"Monitoring {equipment_code}: Elapsed = {elapsed_time:.2f}s, "
            f"Timeout = {timeout}s"
        )
        if elapsed_time > timeout:
            self.trigger_alarm(
                equipment_code, elapsed_time, timeout, "Heartbeat timeout"
            )

    def trigger_alarm(self, equipment_code, elapsed_time, timeout, reason):
        if self.current_alarm_status.get(equipment_code, 0) != 1:
            logging.error(
                f"ALARM TRIGGERED: {reason} for {equipment_code}. "
                f"Elapsed = {elapsed_time:.2f}s, Timeout = {timeout}s"
            )
            self.update_alarm_status(equipment_code, 1)

    def update_alarm_status(self, equipment_code, status):
        if self.current_alarm_status.get(equipment_code) != status:
            self.current_alarm_status[equipment_code] = status
            self.write_alarm_status(equipment_code, status)

    def write_alarm_status(self, equipment_code, status):
        try:
            byte = 8
            bit = 0
            value = status

            self.plc_service.write_alarm(8, byte, bit, value)
            logging.warning(
                f"Alarm written to PLC for {equipment_code}: Byte {byte}, Bit {bit}, Value {value}"
            )
        except Exception as e:
            logging.error(
                f"Failed to write alarm for {equipment_code}: {e}",
                exc_info=True,
            )

    def stop_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()
            logging.info("Heartbeat monitoring stopped.")
