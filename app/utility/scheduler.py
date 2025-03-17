import threading
import logging


class Scheduler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Scheduler, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "timers"):
            self.timers = {}
            self.task_metadata = {}
            self.lock = threading.Lock()

    def schedule_task(
        self, task_id, equipment, action, client, topic_send, interval=None
    ):
        with self.lock:
            if task_id in self.timers:
                self.timers[task_id].cancel()

            interval = interval or ((equipment.p_timer_communication_cycle or 1) * 60)

            def wrapper():
                try:
                    action(client, topic_send, equipment)
                except Exception as e:
                    logging.error(
                        f"Error executing scheduled task '{task_id}': {e}",
                        exc_info=True,
                    )

                with self.lock:
                    if task_id in self.timers:
                        self._reschedule_task(
                            task_id, equipment, action, client, topic_send
                        )

            self._start_timer(task_id, wrapper, interval)

            self.task_metadata[task_id] = {
                "equipment": equipment,
                "interval": interval,
                "action": action,
                "client": client,
                "topic_send": topic_send,
            }
            logging.info(f"Scheduled task '{task_id}' every {interval / 60} minutes.")

    def _start_timer(self, task_id, wrapper, interval):
        timer = threading.Timer(interval, wrapper)
        self.timers[task_id] = timer
        timer.start()

    def update_timer(self, task_id, new_interval_minutes):
        new_interval = new_interval_minutes * 60  # Convert to seconds

        with self.lock:
            if task_id not in self.task_metadata:
                logging.warning(
                    f"Task '{task_id}' not found in metadata. Cannot update."
                )
                return False

            if task_id in self.timers:
                logging.info(f"Canceling old timer for '{task_id}' before updating.")
                self.timers[task_id].cancel()
                del self.timers[task_id]

            metadata = self.task_metadata[task_id]
            equipment = metadata["equipment"]
            self.task_metadata[task_id]["interval"] = new_interval
            equipment.p_timer_communication_cycle = new_interval_minutes

            def wrapper():
                try:
                    metadata["action"](
                        metadata["client"], metadata["topic_send"], equipment
                    )
                except Exception as e:
                    logging.error(
                        f"Error executing scheduled task '{task_id}': {e}",
                        exc_info=True,
                    )

                with self.lock:
                    if task_id in self.timers:
                        self._reschedule_task(
                            task_id,
                            equipment,
                            metadata["action"],
                            metadata["client"],
                            metadata["topic_send"],
                        )

            self._start_timer(task_id, wrapper, new_interval)

            logging.info(
                f"Updated timer for task '{task_id}' with new interval {new_interval / 60} minutes."
            )
            return True

    def _reschedule_task(self, task_id, equipment, action, client, topic_send):
        interval = (equipment.p_timer_communication_cycle or 1) * 60

        def wrapper():
            try:
                action(client, topic_send, equipment)
            except Exception as e:
                logging.error(
                    f"Error executing scheduled task '{task_id}': {e}",
                    exc_info=True,
                )

            with self.lock:
                if task_id in self.timers:
                    self._reschedule_task(
                        task_id, equipment, action, client, topic_send
                    )

        self._start_timer(task_id, wrapper, interval)

    def cancel_task(self, task_id):
        with self.lock:
            if task_id in self.timers:
                self.timers[task_id].cancel()
                del self.timers[task_id]
                logging.info(f"Canceled task '{task_id}' but preserved metadata.")

    def cancel_all_tasks(self):
        with self.lock:
            for task_id, timer in self.timers.items():
                timer.cancel()
            self.timers.clear()
            logging.info("All tasks have been canceled.")
