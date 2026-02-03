"""
In‑process event bus for self‑healing error propagation.
Thread‑safe queue‑based implementation.
"""
import threading
import queue
from typing import Callable, Any, Dict, List

class EventBus:
    """Simple thread‑safe in‑process event bus.
    Subscribers register a callback that receives the event dict.
    """
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def publish(self, event: Dict[str, Any]):
        """Publish an event to the bus."""
        self._queue.put(event)

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a subscriber callback."""
        self._subscribers.append(callback)

    def _worker(self):
        while True:
            event = self._queue.get()
            for cb in self._subscribers:
                try:
                    cb(event)
                except Exception as e:
                    print(f"[EventBus] Subscriber error: {e}")
            self._queue.task_done()

# Singleton instance for easy import
bus = EventBus()
