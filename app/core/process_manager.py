import subprocess
import os
import psutil
from typing import Optional
from app.core.config import settings

class ProcessManager:
    def __init__(self):
        self.script_path = settings.script_path
        self._process: Optional[subprocess.Popen] = None

    def start(self) -> tuple[bool, str]:
        if self.is_running():
            return False, "Process is already running."
        
        if not os.path.exists(self.script_path):
            return False, f"Script not found at {self.script_path}"
        
        try:
            self._process = subprocess.Popen(
                ["python", self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True, f"Process started with PID {self._process.pid}."
        except Exception as e:
            return False, f"Failed to start process: {str(e)}"

    def stop(self) -> tuple[bool, str]:
        if not self.is_running():
            return False, "Process is not running."
        
        try:
            pid = self._process.pid
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            
            self._process.wait(timeout=3)
            self._process = None
            return True, "Process stopped successfully."
        except psutil.NoSuchProcess:
            self._process = None
            return True, "Process was already stopped."
        except Exception as e:
            try:
                parent.kill()
                self._process = None
                return True, "Process killed forcefully."
            except Exception as kill_err:
                return False, f"Failed to stop process: {str(e)} - {str(kill_err)}"

    def is_running(self) -> bool:
        if self._process is None:
            return False

        if self._process.poll() is None:
            return True
        else:
            self._process = None
            return False

    def get_pid(self) -> Optional[int]:
        if self.is_running() and self._process:
            return self._process.pid
        return None

process_manager = ProcessManager()
