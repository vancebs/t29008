import threading
from collections.abc import Callable


class Task(object):
    STATE_IDLE = 0x00000001
    STATE_RUNNING = 0x00000002
    STATE_SUCCESS = 0x00000004
    STATE_ERROR = 0x00000008

    def __init__(self):
        self._state = Task.STATE_IDLE
        self._on_update_state: Callable[[int, int, int, str], None]|None = None
        self._state_cond = threading.Condition()
        self._thread: threading.Thread|None = None

    def state(self) -> int:
        return self._state

    def check_state(self, state: int) -> bool:
        return self._state & state != 0

    def wait_for_state(self, state: int):
        while not self.check_state(state):
            with self._state_cond:
                self._state_cond.wait()

    def set_state(self, state: int, cur_progress: int = 0, max_progress: int = 0, message: str|None = None):
        if self._state == state and state != Task.STATE_RUNNING:
            return

        with self._state_cond:
            self._state = state
            self._state_cond.notify_all()

        self.notify_state_update(self._state, cur_progress, max_progress, message)

    def start(self):
        self._thread = threading.Thread(target=self.on_start)
        self._thread.start()

    def wait_for_finished(self):
        if self._thread:
            self._thread.join()

    def set_state_update_listener(self, listener: Callable[[int, int, int, str], None]):
        self._on_update_state = listener

    def notify_state_update(self, state: int, cur_progress: int = 0, max_progress: int = 0, message: str|None = None):
        if self._on_update_state:
            self._on_update_state(state, cur_progress, max_progress, message)

    def on_start(self) -> bool:
        pass