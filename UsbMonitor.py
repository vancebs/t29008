import os
import platform
import re
import subprocess
import time
from typing import Callable, Set, Union

from Application import Application


class BaseUsbMonitor(object):
    def __init__(self):
        self._stopped = True
        self._on_arrival: Union[Callable[[str], None], None] = None
        self._on_removed: Union[Callable[[str], None], None] = None

    def start(self):
        if not self._stopped:
            return
        self._stopped = False
        self.on_start()

    def stop(self):
        if self._stopped:
            return
        self._stopped = True
        self.on_stop()

    def set_arrival_listener(self, listener: Callable[[str], None]):
        self._on_arrival = listener

    def set_removed_listener(self, listener: Callable[[str], None]):
        self._on_removed = listener

    def notify_arrival(self, port: str):
        if self._on_arrival:
            self._on_arrival(port)

    def notify_removed(self, port: str):
        if self._on_removed:
            self._on_removed(port)

    def on_start(self):
        pass

    def on_stop(self):
        pass


class PollingUsbMonitor(BaseUsbMonitor):
    def __init__(self):
        super().__init__()
        self._ports: Set[str] = set()

    def on_start(self):
        while not self._stopped:
            new_ports: Set[str] = self.on_polling()

            # notify removed
            for port in (self._ports - new_ports):
                self.notify_removed(port)

            # notify arrival
            for port in (new_ports - self._ports):
                self.notify_arrival(port)

            # update ports
            self._ports = new_ports

            # check for every 1 second
            time.sleep(1)

    def on_polling(self) -> Set[str]:
        pass


class WindowsUsbMonitor(PollingUsbMonitor):
    PATTERN_USB_LINE = re.compile(r'\s*Qualcomm\s+HS-USB\s+QDLoader\s+9008\s+\((?P<port>COM\d+)\)\s*')

    def __init__(self):
        super().__init__()
        self._cmd = os.path.join(Application.get().tool_dir(), 'lsusb.exe')

    def on_polling(self):
        ports: Set[str] = set()

        # run lsusb.exe
        lsusb = subprocess.Popen([self._cmd], stdout=subprocess.PIPE, universal_newlines=True)
        for line in lsusb.stdout:
            matched = WindowsUsbMonitor.PATTERN_USB_LINE.match(line)
            if matched:
                ports.add(matched['port'])
        lsusb.wait()

        return ports


class LinuxUsbMonitor(PollingUsbMonitor):
    PATTERN_ATTACH_LINE = re.compile(r'\s*.+:\s+Qualcomm\s+USB\s+modem\s+converter\s+now\s+attached\s+to\s+(?P<port>ttyUSB\d+)\s*')
    PATTERN_DETACH_LINE = re.compile(r'\s*.+:\s+Qualcomm\s+USB\s+modem\s+converter\s+now\s+disconnected\s+from\s+(?P<port>ttyUSB\d+)\s*')

    def __init__(self):
        super().__init__()

    def on_polling(self):
        ports: Set[str] = set()

        # run "dmesg | grep tty"
        proc = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE, universal_newlines=True)
        for line in proc.stdout:
            matched = LinuxUsbMonitor.PATTERN_ATTACH_LINE.match(line)
            if matched:
                ports.add(matched['port'])
                continue

            matched = LinuxUsbMonitor.PATTERN_DETACH_LINE.match(line)
            if matched:
                ports.remove(matched['port'])

        proc.wait()

        return ports


os_name = platform.system()
if os_name == 'Windows':
    UsbMonitor = WindowsUsbMonitor
elif os_name == 'Linux':
    UsbMonitor = LinuxUsbMonitor
