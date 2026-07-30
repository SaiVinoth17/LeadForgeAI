import threading
import queue
import time
from core.logger import logger

class TaskManager:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        
    def _worker(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1.0)
                try:
                    task_func, args, kwargs = task
                    task_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Task failed: {e}")
                finally:
                    self.task_queue.task_done()
            except queue.Empty:
                continue

    def add_task(self, func, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))
        
    def shutdown(self):
        self.running = False
        self.worker_thread.join(timeout=2.0)

task_manager = TaskManager()
