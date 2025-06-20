import os.path
from typing import Dict, Union

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

    def on_stop_progress(self, key: str, success: bool, message: Union[str, None]):
        pass

    def on_update_progress(self, key: str, cur_progress: int, max_progress: Union[int, None]):
        pass


class T2Edl(object):
    STATE_IDLE = 0
    STATE_STARTED = 1


    def __init__(self,
                 image_dir: str,
                 reboot_on_success: bool = False,
                 trace_dir: str = os.path.join(Application.get().application_dir(), 'port_trace'),
                 max_download_count: int = 0,
                 prog: str = 'prog_firehose_ddr.elf',
                 is_vip: Union[bool, None] = None,
                 signed_digests: Union[str, None] = None,
                 chained_digests: Union[str, None] = None,
                 disable_zeroout: bool = False,
                 disable_erase: bool = False):
        self._image_dir = image_dir
        self._reboot_on_success = reboot_on_success
        self._trace_dir = trace_dir
        self._max_download_count = max_download_count
        self._prog = prog
        self._is_vip = is_vip
        self._signed_digests = signed_digests
        self._chained_digests = chained_digests
        self._disable_zeroout = disable_zeroout
        self._disable_erase = disable_erase

        self._started_task_count = 0

        self._watcher: Union[Watcher, None] = None

        self._stopped = True
        self._running_tasks: Dict[str, Task] = dict()

        self._monitor = UsbMonitor()
        self._monitor.set_arrival_listener(lambda port: self.on_arrival(port))
        self._monitor.set_removed_listener(lambda port: self.on_removed(port))

    def verify_vip(self) -> bool:
        # check vip
        if self._is_vip is None:
            # auto find signed digests and chained digests if not set
            self._signed_digests = T2EdlTask.param_signeddigests(self._image_dir, self._signed_digests)
            self._chained_digests = T2EdlTask.param_chaineddigests(self._image_dir, self._chained_digests)

            # enable vip if both signed digests and chained digests files are exists
            self._is_vip = self._signed_digests is not None and self._chained_digests is not None
        elif self._is_vip:
            # auto find signed digests and chained digests if not set
            self._signed_digests = T2EdlTask.param_signeddigests(self._image_dir, self._signed_digests)
            self._chained_digests = T2EdlTask.param_chaineddigests(self._image_dir, self._chained_digests)

            if self._signed_digests is None:
                self.notify_error_message('signeddigests file not exists!!')
                return False
            if self._chained_digests is None:
                self.notify_error_message('chaineddigests file not exists!!')
                return False
        else: # self._is_vip == False
            self._signed_digests = None
            self._chained_digests = None

        # show vip status
        if self._is_vip:
            self.notify_warning_message('VIP: ON')
        else:
            self.notify_info_message('VIP: OFF')

        return True

    def on_task_state_updated(self,
                              key: str,
                              task: Task,
                              state: int,
                              cur_progress: int,
                              max_progress: int,
                              message: Union[str, None]):
        if state == Task.STATE_IDLE:
            if message:
                self.notify_message(f'[red][{key}] {message}')
            self.notify_update_progress(key)
        elif state == Task.STATE_RUNNING:
            if message:
                self.notify_message(f'[red][{key}] {message}')
            self.notify_update_progress(key, cur_progress, max_progress)
        elif state == Task.STATE_SUCCESS:
            self.notify_stop_progress(key, True, message)
        elif state == Task.STATE_ERROR:
            self.notify_stop_progress(key, False, message)

    def start(self):
        if not self._stopped:
            return
        self._stopped = False

        # title
        self.notify_warning_message(f'Usage:')
        self.notify_warning_message(f'    1. Switch device to 9008 mode and connect to PC with USB.')
        self.notify_warning_message(f'    2. Download will auto start once device connected.')
        self.notify_warning_message(f'    3. Connect more device for multi-downloading.')
        self.notify_warning_message(f'    4. Ctrl + C to stop. t29008 will exit after all downloading finished.')
        self.notify_warning_message(f'-------------------------------------------------------------------------')

        # verify parameter
        if not os.path.exists(self._image_dir):
            self.notify_error_message(f'Image path not exists: {self._image_dir}')
            return  # failed

        # get real path
        self._image_dir = os.path.realpath(self._image_dir)
        self._trace_dir = os.path.realpath(self._trace_dir)

        # print path
        self.notify_info_message(f'Image Path: {self._image_dir}')
        self.notify_info_message(f'trace Dir: {self._trace_dir}')

        # verify VIP
        if not self.verify_vip():
            self._stopped = True
            return  # failed

        # show starting
        self.notify_started()
        self.notify_info_message('Start downloading...')

        # start UsbMonitor
        self._monitor.start()

        # stop
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
                         reboot_on_success=self._reboot_on_success,
                         prog=self._prog,
                         is_vip=self._is_vip,
                         signed_digests=self._signed_digests,
                         chained_digests=self._chained_digests,
                         disable_zeroout=self._disable_zeroout,
                         disable_erase=self._disable_erase)
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

    def notify_stop_progress(self, key: str, success: bool, message: Union[str, None]):
        if self._watcher:
            self._watcher.on_stop_progress(key, success, message)

    def notify_update_progress(self, key: str, cur_progress: int = 0, max_progress: Union[int, None] = None):
        if self._watcher:
            self._watcher.on_update_progress(key, cur_progress, max_progress)
