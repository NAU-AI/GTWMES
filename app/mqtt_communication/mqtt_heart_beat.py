import threading
import time
import datetime
from sqlalchemy.orm import Session
from model.dto.equipment_dto import EquipmentDTO
from service.equipment_service import EquipmentService
from service.plc_service import PlcService
from utility.logger import Logger

logger = Logger.get_logger(__name__)


class MqttHeartbeatMonitor:
    GRACE_PERIOD = 5

    def __init__(self, session: Session, plc_service=None, equipment_service=None):
        self.last_heartbeats = {}
        self.previous_cycles = {}
        self.current_alarm_status = {}

        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.monitor_thread = None

        self.plc_service = plc_service or PlcService(session)
        self.equipment_service = equipment_service or EquipmentService(session)

    def received_heartbeat(self, equipment_code):
        with self.lock:
            previous_heartbeat = self.last_heartbeats.get(equipment_code)
            self.last_heartbeats[equipment_code] = time.time()
            self.update_alarm_status(equipment_code, False)

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
                "Heartbeat received for %s. Previous: %s, New: %s",
                equipment_code,
                previous_heartbeat_str,
                new_heartbeat_str,
            )

    def start_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return

        logger.info("Starting heartbeat monitor thread.")

        def monitor():
            try:
                while not self.stop_event.is_set():
                    equipments = self.equipment_service.get_all_equipment()

                    with self.lock:
                        for equipment in equipments:
                            self._process_equipment_heartbeat(equipment)

                    time.sleep(60)
            except Exception as e:
                logger.error(
                    "Unexpected error in heartbeat monitor: %s", e, exc_info=True
                )

        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()

        logger.info("Heartbeat monitoring started.")

    def _process_equipment_heartbeat(self, equipment: EquipmentDTO):
        equipment_code = equipment.code
        current_cycle = equipment.p_timer_communication_cycle

        if equipment_code not in self.last_heartbeats:
            self.last_heartbeats[equipment_code] = time.time()
            self.current_alarm_status[equipment_code] = 0
            logger.info("Initialized heartbeat tracking for %s.", equipment_code)
            return

        last_heartbeat = self.last_heartbeats[equipment_code]

        self._check_heartbeat_timeout(equipment_code, last_heartbeat, current_cycle)

    def _check_heartbeat_timeout(self, equipment_code, last_heartbeat, current_cycle):
        timeout = (3 * current_cycle * 60) + self.GRACE_PERIOD
        elapsed_time = time.time() - last_heartbeat

        logger.debug(
            "Monitoring %s: Elapsed = %.2fs, Timeout = %ss",
            equipment_code,
            elapsed_time,
            timeout,
        )

        if elapsed_time > timeout:
            self._trigger_alarm(equipment_code, elapsed_time, timeout)

    def _trigger_alarm(self, equipment_code, elapsed_time, timeout):
        if self.current_alarm_status.get(equipment_code, 0) == 1:
            return

        logger.error(
            "ALARM TRIGGERED: Heartbeat timeout for %s. Elapsed = %.2fs, Timeout = %ss",
            equipment_code,
            elapsed_time,
            timeout,
        )

        self.update_alarm_status(equipment_code, True)

    def update_alarm_status(self, equipment_code, status: bool):
        if self.current_alarm_status.get(equipment_code) != status:
            self.current_alarm_status[equipment_code] = status
            self._write_alarm_status(equipment_code, status)

    def _write_alarm_status(self, equipment_code, status: bool):
        try:
            self.plc_service.write_alarm_status_by_key(
                equipment_code=equipment_code, key="PLC_ALARM", status=status
            )
            logger.warning(
                "Alarm 'Plc_alarm' written to PLC for %s: %s",
                equipment_code,
                status,
            )
        except Exception as e:
            logger.error(
                "Failed to write alarm for %s: %s", equipment_code, e, exc_info=True
            )

    def stop_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.stop_event.set()
            self.monitor_thread.join()
            logger.info("Heartbeat monitoring stopped.")
