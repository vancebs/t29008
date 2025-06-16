import os
import platform
import re
import subprocess
from datetime import datetime
from typing import Callable, Tuple

from Application import Application
from Task import Task


class T2EdlTask(Task):
    PATTERN_FH_LOADER_PERCENT_LINE = re.compile(r'\s*\d{2}:\d{2}:\d{2}:\s+\w+:\s+\{percent\s+files\s+transferred\s+(?P<percent>\d+\.\d+)%}\s*')

    PATTERN_RAWPROGRAM = re.compile(r'rawprogram\d+.xml')
    PATTERN_PATCH = re.compile(r'patch\d+.xml')

    SIGNEDDIGESTS_SEARCH_LIST_WINDOWS = (
        'DigestsSignedZlpAwareHost.bin.mbn',
        'DigestsSigned.bin.mbn',
        'DigestsToSign.bin.mbn'
    )

    SIGNEDDIGESTS_SEARCH_LIST_LINUX = (
        'DigestsSigned.bin.mbn',
        'DigestsToSign.bin.mbn'
    )

    SIGNEDDIGESTS_SEARCH_LIST = SIGNEDDIGESTS_SEARCH_LIST_WINDOWS if platform.system() == 'Windows' else SIGNEDDIGESTS_SEARCH_LIST_LINUX

    CHAINEDDIGESTS_SEARCH_LIST_WINDOWS = (
        'ChainedTableOfDigestsZlpAwareHost.bin',
        'ChainedTableOfDigests.bin'
    )

    CHAINEDDIGESTS_SEARCH_LIST_LINUX = (
        'ChainedTableOfDigests.bin',
    )

    CHAINEDDIGESTS_SEARCH_LIST = CHAINEDDIGESTS_SEARCH_LIST_WINDOWS if platform.system() == 'Windows' else CHAINEDDIGESTS_SEARCH_LIST_LINUX

    def __init__(self,
                 port: str,
                 image_dir: str,
                 trace_dir: str,
                 is_vip: bool = False,
                 reboot_on_success: bool = False,
                 prog: str = 'prog_firehose_ddr.elf',
                 signed_digests: str | None = None,
                 chained_digests: str | None = None):
        super().__init__()

        self._port = port
        self._image_dir = image_dir
        self._trace_dir = trace_dir
        self._is_vip = is_vip
        self._reboot_on_success = reboot_on_success
        self._prog = prog
        self._signed_digests = signed_digests
        self._chained_digests = chained_digests

        self._slash = '\\' if platform.system() == 'Windows' else '/'
        if not self._image_dir.endswith(self._slash):
            self._image_dir = self._image_dir + self._slash

    def on_start(self) -> bool:
        self.set_state(Task.STATE_RUNNING)

        if not os.path.exists(self._trace_dir):
            os.makedirs(self._trace_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[0:-3]
        sahara_trace = os.path.join(self._trace_dir, f'{timestamp}_{self._port}_sahara.log')
        fh_loader_trace = os.path.join(self._trace_dir, f'{timestamp}_{self._port}_fh_loader.log')

        result, msg = self.download_sahara(sahara_trace)
        if not result:
            self.set_state(Task.STATE_ERROR, message=msg)
            return False

        result, msg = self.download_fh_loader(fh_loader_trace)
        if not result:
            self.set_state(Task.STATE_ERROR, message=msg)
            return False

        self.set_state(Task.STATE_SUCCESS, message=msg)

        return True

    def download_sahara(self, trace_file: str) -> Tuple[bool, str]:
        cmd = [
            T2EdlTask.bin_sahara(),
            '-p', T2EdlTask.param_port(self._port),
            '-s', f'13:{self._prog}',
            '-b', self._image_dir
        ]

        # run sahara
        sahara = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding=T2EdlTask.encoding()
        )
        sahara.wait()

        # save logs
        with open(trace_file, 'w') as file:
            file.write(f'cmd: {' '.join(cmd)}\n\n')
            file.write(sahara.stdout.read())

        # result
        return sahara.returncode == 0, os.path.realpath(trace_file)

    def download_fh_loader(self, trace_file: str) -> Tuple[bool, str]:
        # cmd
        cmd = [
            T2EdlTask.bin_fh_loader(),
            f'--port={T2EdlTask.param_port(self._port)}',
            f'--sendxml={T2EdlTask.param_sendxml(self._image_dir)}',
            f'--search_path={self._image_dir}',
            '--showpercentagecomplete',
            '--memoryname=ufs',
            '--setactivepartition=1',
            f'--zlpawarehost={T2EdlTask.param_zlpawarehost()}',
            f'--porttracename={trace_file}'
        ]
        if self._is_vip:
            # find signeddigests
            if self._signed_digests is None:
                self._signed_digests = T2EdlTask.param_signeddigests(self._image_dir)
                if self._signed_digests is None:
                    return False, 'signeddigests file not exists'

            # find chaineddigests
            if self._chained_digests is None:
                self._chained_digests = T2EdlTask.param_chaineddigests(self._image_dir)
                if self._chained_digests is None:
                    return False, 'chaineddigests file not exists'

            cmd.extend([
                f'--signeddigests={self._signed_digests}',
                f'--chaineddigests={self._chained_digests}'])
        if self._reboot_on_success:
            cmd.append('--power=reset,1')

        # run fh_loader
        fh_loader = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=T2EdlTask.encoding()
        )

        # write \n to pass 'Press any key to exit' when error
        fh_loader.stdin.write('\n')
        fh_loader.stdin.flush()

        # progress
        for line in fh_loader.stdout:
           self.parse_hf_loader_line(line)

        # result
        fh_loader.wait()
        return fh_loader.returncode == 0, os.path.realpath(trace_file)

    def parse_hf_loader_line(self, line: str):
        matched = T2EdlTask.PATTERN_FH_LOADER_PERCENT_LINE.match(line)
        if matched:
            progress_str = matched['percent']
            progress = int(float(progress_str) * 100)
            self.set_state(Task.STATE_RUNNING, progress, 10000)

    @staticmethod
    def bin_sahara():
        return os.path.join(Application.get().tool_dir(), 'QSaharaServer.exe' if platform.system() == 'Windows' else 'QSaharaServer')

    @staticmethod
    def bin_fh_loader():
        return os.path.join(Application.get().tool_dir(), 'fh_loader.exe' if platform.system() == 'Windows' else 'fh_loader')

    @staticmethod
    def param_port(port: str) -> str:
        match platform.system():
            case 'Windows':
                return f'\\\\.\\{port}'
            case 'Linux':
                return f'/dev/{port}'
            case _:
                return port

    @staticmethod
    def param_sendxml(image_dir: str) -> str:
        file_list = os.listdir(image_dir)
        raw_programs = [filename for filename in file_list if T2EdlTask.PATTERN_RAWPROGRAM.match(filename)]
        patches = [filename for filename in file_list if T2EdlTask.PATTERN_PATCH.match(filename)]
        return ','.join([*sorted(raw_programs), *sorted(patches)])

    @staticmethod
    def param_zlpawarehost() -> str:
        return '1' if platform.system() == 'Windows' else '0'

    @staticmethod
    def param_signeddigests(image_dir: str) -> str|None:
        file_list = os.listdir(image_dir)
        for filename in T2EdlTask.SIGNEDDIGESTS_SEARCH_LIST:
            if filename in file_list:
                return filename
        return None

    @staticmethod
    def param_chaineddigests(image_dir: str) -> str|None:
        file_list = os.listdir(image_dir)
        for filename in T2EdlTask.CHAINEDDIGESTS_SEARCH_LIST:
            if filename in file_list:
                return filename
        return None

    @staticmethod
    def encoding():
        return 'gbk' if platform.system() == 'Windows' else 'utf8'

    @staticmethod
    def read_line_ex(process: subprocess.Popen, callback: Callable[[str], None]):
        line: bytes = bytes()
        encoding = T2EdlTask.encoding()

        while process.poll() is None:
            char = process.stdout.read(1)
            if char in (b'\r', b'\n'):
                callback(line.decode(encoding))
                line = bytes()
            else:
                line += char





