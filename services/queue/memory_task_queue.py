import threading
import logging
from services.queue.task_queue import TaskQueue

class InMemoryTaskQueue(TaskQueue):
    """
    An in-memory implementation of a task queue.
    
    This class provides thread-safe queue operations using Python's threading module.
    It stores tasks in memory and is suitable for single-process applications.
    
    Attributes:
        _queue (list): The list storing queued tasks
        _lock (threading.Lock): Lock for thread-safe operations
        logger (logging.Logger): Logger instance for queue operations
    """
    def __init__(self):
        """
        Initialize the in-memory task queue.
        
        Creates an empty queue and initializes the threading lock and logger.
        """
        self._queue = []
        self._lock = threading.Lock()
        self.logger = logging.getLogger(InMemoryTaskQueue.__name__)

    def enqueue(self, task):
        """
        Add a task to the queue.
        
        Args:
            task (object): The task object to be added to the queue
        """
        with self._lock:
            self._queue.append(task)
            self.logger.debug("Task enqueued %s", task.__class__.__name__)

    def dequeue(self):
        """
        Remove and return a task from the queue.
        
        Returns:
            object: The next task in the queue, or None if the queue is empty
        """
        with self._lock:
            if not self._queue:
                self.logger.debug("Queue is empty")
                return None
            return self._queue.pop(0)
