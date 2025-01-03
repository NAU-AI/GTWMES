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

    def schedule_task(self, task_id, equipment, action, client, topic_send):
        with self.lock:
            if task_id in self.timers:
                self.timers[task_id].cancel()

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
                        interval = equipment.p_timer_communication_cycle
                        self._reschedule_task(
                            task_id, equipment, action, client, topic_send, interval
                        )

            interval = equipment.p_timer_communication_cycle
            self._start_timer(task_id, wrapper, interval)

            self.task_metadata[task_id] = {
                "equipment": equipment,
                "interval": interval,
                "action": action,
                "client": client,
                "topic_send": topic_send,
            }
            logging.info(f"Scheduled task '{task_id}' every {interval}s.")

    def _start_timer(self, task_id, wrapper, interval):
        timer = threading.Timer(interval, wrapper)
        self.timers[task_id] = timer
        timer.start()

    def update_timer(self, task_id, new_interval):
        with self.lock:
            if task_id not in self.task_metadata:
                logging.warning(
                    f"Task '{task_id}' not found in metadata. Cannot update."
                )
                return False

            if task_id in self.timers:
                self.timers[task_id].cancel()
                del self.timers[task_id]

            metadata = self.task_metadata[task_id]
            equipment = metadata["equipment"]
            self.task_metadata[task_id]["interval"] = new_interval
            equipment.p_timer_communication_cycle = new_interval

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
                        interval = equipment.p_timer_communication_cycle
                        self._reschedule_task(
                            task_id,
                            equipment,
                            metadata["action"],
                            metadata["client"],
                            metadata["topic_send"],
                            interval,
                        )

            interval = new_interval
            self._start_timer(task_id, wrapper, interval)

            logging.info(
                f"Updated timer for task '{task_id}' with new interval {new_interval}s."
            )
            return True

    def _reschedule_task(
        self, task_id, equipment, action, client, topic_send, interval
    ):
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
                        task_id,
                        equipment,
                        action,
                        client,
                        topic_send,
                        equipment.p_timer_communication_cycle,
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
