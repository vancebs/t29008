import os
import sys
from typing import Union


class Application(object):
    _sInstance: 'Union[Application, None]' = None

    @staticmethod
    def init(application_dir: str):
        Application._sInstance = Application(application_dir)

    @staticmethod
    def get() -> 'Application':
        if Application._sInstance is None:
            Application._sInstance = Application()
        return Application._sInstance

    def __init__(self, script_dir: str = os.path.dirname(os.path.realpath(__file__))):
        self._application_dir = os.path.basename(sys.argv[0])
        self._working_dir = os.getcwd()
        self._script_dir = script_dir
        self._misc_dir = os.path.join(self._script_dir, 'misc')
        self._tool_dir = os.path.join(self._misc_dir, 'vip_download_tool')

    def application_dir(self) -> str:
        return self._application_dir

    def working_dir(self) -> str:
        return self._working_dir

    def script_dir(self):
        return self._script_dir

    def misc_dir(self) -> str:
        return self._misc_dir

    def tool_dir(self) -> str:
        return self._tool_dir
