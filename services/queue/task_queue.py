from abc import ABC, abstractmethod

class TaskQueue(ABC):
    """
    Abstract base class defining the interface for a task queue.
    
    This class defines the contract for task queue implementations,
    requiring them to provide enqueue and dequeue operations.
    """
    @abstractmethod
    def enqueue(self, task : object) -> None:
        """
        Add a task to the queue.
        
        Args:
            task (object): The task object to be added to the queue
        """
    @abstractmethod
    def dequeue(self) -> object:
        """
        Remove and return a task from the queue.
        
        Returns:
            object: The next task in the queue
        """
