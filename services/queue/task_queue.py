from abc import ABC, abstractmethod

class TaskQueue(ABC):
    @abstractmethod
    def enqueue(self, task : object) -> None:
        """Enqueue task"""
    @abstractmethod
    def dequeue(self) -> object:
        """Enqueue task"""