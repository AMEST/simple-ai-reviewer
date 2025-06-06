import threading
import logging
from services.queue.task_queue import TaskQueue

class InMemoryTaskQueue(TaskQueue):
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self.logger = logging.getLogger(InMemoryTaskQueue.__name__)

    def enqueue(self, task):
        with self._lock:
            self._queue.append(task)
            self.logger.debug("Task enqueued %s", task.__class__.__name__)

    def dequeue(self):
        with self._lock:
            if not self._queue:
                self.logger.debug("Queue is empty")
                return None
            return self._queue.pop(0)
