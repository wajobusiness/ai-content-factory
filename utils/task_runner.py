"""
Asynchronous Background Task Manager for AI Content Factory SaaS.
Enables tasks to continue executing across page navigations with real-time status and cancellation support.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, List
from utils.helpers import logger


class TaskCancelledException(Exception):
    """Raised when a running task is cancelled by the user."""
    pass


class TaskState:
    """Thread-safe state container for a background job."""

    def __init__(self, task_id: str, name: str):
        self.task_id = task_id
        self.name = name
        self.status = "running"  # running, completed, failed, cancelled
        self.progress = 0.0      # 0.0 to 1.0
        self.current_step = "Initializing..."
        self.logs: List[str] = [f"[{time.strftime('%H:%M:%S')}] Task '{name}' initialized."]
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.cancel_event = threading.Event()
        self.lock = threading.Lock()

    def update_step(self, step_name: str, progress: float, log_msg: Optional[str] = None):
        """Updates current execution step and progress."""
        with self.lock:
            self.current_step = step_name
            self.progress = max(0.0, min(1.0, progress))
            ts = time.strftime('%H:%M:%S')
            entry = f"[{ts}] {log_msg or step_name}"
            self.logs.append(entry)
            if len(self.logs) > 50:
                self.logs.pop(0)

    def check_cancelled(self):
        """Checks if cancellation has been requested."""
        if self.cancel_event.is_set():
            raise TaskCancelledException(f"Task '{self.name}' was cancelled by user.")

    def cancel(self):
        """Signals cancellation to the running task."""
        with self.lock:
            self.cancel_event.set()
            self.status = "cancelled"
            self.end_time = time.time()
            self.logs.append(f"[{time.strftime('%H:%M:%S')}] 🛑 Task cancelled by user.")

    def complete(self, result: Dict[str, Any]):
        """Marks task as successfully completed."""
        with self.lock:
            self.status = "completed"
            self.progress = 1.0
            self.current_step = "Completed"
            self.result = result
            self.end_time = time.time()
            self.logs.append(f"[{time.strftime('%H:%M:%S')}] ✅ Task finished successfully.")

    def fail(self, error: str):
        """Marks task as failed."""
        with self.lock:
            self.status = "failed"
            self.error = error
            self.end_time = time.time()
            self.logs.append(f"[{time.strftime('%H:%M:%S')}] ❌ Error: {error}")

    def get_summary(self) -> Dict[str, Any]:
        """Returns clean serializable dictionary of state."""
        with self.lock:
            elapsed = (self.end_time or time.time()) - self.start_time
            return {
                "task_id": self.task_id,
                "name": self.name,
                "status": self.status,
                "progress": self.progress,
                "current_step": self.current_step,
                "logs": list(self.logs),
                "elapsed_seconds": round(elapsed, 1),
                "is_active": self.status == "running",
                "result": self.result,
                "error": self.error
            }


class BackgroundTaskManager:
    """Singleton background worker and task lifecycle coordinator."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BackgroundTaskManager, cls).__new__(cls)
                cls._instance._tasks: Dict[str, TaskState] = {}
                cls._instance._active_task_id: Optional[str] = None
        return cls._instance

    def start_pipeline_task(
        self,
        task_name: str,
        target_fn: Callable[..., Any],
        kwargs: Dict[str, Any]
    ) -> str:
        """Launches a function in a background daemon thread."""
        task_id = f"task_{int(time.time() * 1000)}"
        state = TaskState(task_id=task_id, name=task_name)
        
        with self._lock:
            self._tasks[task_id] = state
            self._active_task_id = task_id

        def worker():
            try:
                logger.info(f"Background worker started for task '{task_name}' ({task_id})")
                # Inject cancel_event and progress_callback into kwargs if supported
                kwargs["cancel_event"] = state.cancel_event
                kwargs["progress_callback"] = state.update_step
                
                result = target_fn(**kwargs)
                state.complete(result)
            except TaskCancelledException as ce:
                logger.warning(f"Task '{task_name}' cancelled: {ce}")
                state.cancel()
            except Exception as e:
                logger.error(f"Task '{task_name}' failed with error: {e}", exc_info=True)
                state.fail(str(e))

        thread = threading.Thread(target=worker, daemon=True, name=f"Worker-{task_id}")
        thread.start()
        return task_id

    def cancel_active_task(self) -> bool:
        """Cancels the currently running background task."""
        with self._lock:
            if self._active_task_id and self._active_task_id in self._tasks:
                task = self._tasks[self._active_task_id]
                if task.status == "running":
                    task.cancel()
                    return True
        return False

    def get_active_task(self) -> Optional[TaskState]:
        """Returns the active TaskState or the most recent one."""
        with self._lock:
            if self._active_task_id and self._active_task_id in self._tasks:
                return self._tasks[self._active_task_id]
        return None

    def clear_active_task(self):
        """Clears active task pointer."""
        with self._lock:
            self._active_task_id = None


# Global singleton instance
task_manager = BackgroundTaskManager()
