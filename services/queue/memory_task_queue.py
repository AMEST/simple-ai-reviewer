from services.queue.task_queue import TaskQueue
import threading

class InMemoryTaskQueue(TaskQueue):
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()

    def enqueue(self, task):
        with self._lock:
            self._queue.append(task)

    def dequeue(self):
        with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)
