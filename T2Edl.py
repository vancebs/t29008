import os.path
import threading
from datetime import datetime
from typing import Dict

from Application import Application
from T2EdlTask import T2EdlTask
from Task import Task
from UsbMonitor import UsbMonitor


class Watcher(object):
    def on_started(self):
        pass

    def on_stopped(self):
        pass

    def on_update_message(self, message: str, color: str):
        pass

    def on_start_progress(self, key: str):
        pass

    def on_stop_progress(self, key: str, success: bool, message: str|None):
        pass

    def on_update_progress(self, key: str, cur_progress: int, max_progress: int|None):
        pass


class T2Edl(object):
    STATE_IDLE = 0
    STATE_STARTED = 1


    def __init__(self,
                 image_dir: str,
                 is_vip: bool = False,
                 reboot_on_success: bool = False,
                 trace_dir: str = os.path.join(Application.get().application_dir(), 'port_trace'),
                 max_download_count: int = 0,
                 prog: str = 'prog_firehose_ddr.elf',
                 signed_digests: str|None = None,
                 chained_digests: str|None = None):
        self._image_dir = image_dir
        self._is_vip = is_vip
        self._reboot_on_success = reboot_on_success
        self._trace_dir = trace_dir
        self._max_download_count = max_download_count
        self._prog = prog
        self._signed_digests = signed_digests
        self._chained_digests = chained_digests

        self._started_task_count = 0

        self._watcher: Watcher|None = None

        self._stopped = True
        self._running_tasks: Dict[str, Task] = dict()

        self._monitor = UsbMonitor()
        self._monitor.set_arrival_listener(lambda port: self.on_arrival(port))
        self._monitor.set_removed_listener(lambda port: self.on_removed(port))

    def on_task_state_updated(self, key: str, task: Task, state: int, cur_progress: int, max_progress: int, message: str|None):
        match state:
            case Task.STATE_IDLE:
                if message:
                    self.notify_message(f'[red][{key}] {message}')
                self.notify_update_progress(key)
            case Task.STATE_RUNNING:
                if message:
                    self.notify_message(f'[red][{key}] {message}')
                self.notify_update_progress(key, cur_progress, max_progress)
            case Task.STATE_SUCCESS:
                self.notify_stop_progress(key, True, message)
            case Task.STATE_ERROR:
                self.notify_stop_progress(key, False, message)

    def start(self):
        if not self._stopped:
            return
        self._stopped = False

        self.notify_started()
        self.notify_info_message('Start downloading...')

        # start UsbMonitor
        self._monitor.start()

        self.stop()

    def stop(self):
        if self._stopped:
            return  # already stopped

        self._stopped = True
        self._monitor.stop()
        self.notify_info_message('Application will stop after all downloading finished!!')
        for task in self._running_tasks.values():
            #task.wait_for_state(Task.STATE_SUCCESS | Task.STATE_ERROR)
            task.wait_for_finished()
        self.notify_stopped()

    def on_arrival(self, port: str):
        if port in self._running_tasks:
            self.notify_warning_message(f'[{port}] arrived while already started downloading.')
            return # already started

        self.notify_start_progress(port)
        task = T2EdlTask(port,
                         self._image_dir,
                         self._trace_dir,
                         is_vip=self._is_vip,
                         reboot_on_success=self._reboot_on_success,
                         prog=self._prog,
                         signed_digests=self._signed_digests,
                         chained_digests=self._chained_digests)
        self._running_tasks[port] = task
        task.set_state_update_listener(
            lambda state, cur_progress, max_progress, message: self.on_task_state_updated(port, task, state,
                                                                                          cur_progress, max_progress,
                                                                                          message))
        task.start()

        self._started_task_count += 1
        if 0 < self._max_download_count <= self._started_task_count:
            self.notify_info_message(f'Auto stop due to max download count({self._max_download_count}) reached.')
            self.stop()

    def on_removed(self, port: str):
        if port not in self._running_tasks:
            self.notify_warning_message(f'[{port}] removed while not started downloading.')
            return  # already started

        self._running_tasks[port].wait_for_finished()
        del self._running_tasks[port]

    def watch(self, watcher: Watcher):
        self._watcher = watcher

    def notify_started(self):
        if self._watcher:
            self._watcher.on_started()

    def notify_stopped(self):
        if self._watcher:
            self._watcher.on_stopped()

    def notify_message(self, message: str, color='blue'):
        if self._watcher:
            self._watcher.on_update_message(message, color)

    def notify_info_message(self, message: str):
        self.notify_message(message, 'blue')

    def notify_warning_message(self, message: str):
        self.notify_message(message, 'yellow')

    def notify_error_message(self, message: str):
        self.notify_message(message, 'red')

    def notify_start_progress(self, key: str):
        if self._watcher:
            self._watcher.on_start_progress(key)

    def notify_stop_progress(self, key: str, success: bool, message: str|None):
        if self._watcher:
            self._watcher.on_stop_progress(key, success, message)

    def notify_update_progress(self, key: str, cur_progress: int = 0, max_progress: int|None = None):
        if self._watcher:
            self._watcher.on_update_progress(key, cur_progress, max_progress)
