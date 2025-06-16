from typing import Dict

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TaskID

from T2Edl import Watcher


class T2EdlUi(Watcher):
    def __init__(self):
        self._console = Console(record=True)
        self._progress = Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
                console=self._console,
                transient=False,
        )
        self._tasks: Dict[str, TaskID] = dict()

    def on_started(self):
        self._progress.start()

    def on_stopped(self):
        self._progress.stop()

    def on_update_message(self, message: str, color: str):
        self._console.log(f'[{color}]{message}')

    def on_start_progress(self, key: str):
        self._tasks[key] = self._progress.add_task(f'[green]{key}', total=None)

    def on_stop_progress(self, key: str, success: bool, message: str|None):
        if key not in self._tasks:
            self._console.log(f'Invalid device: {key} ({message})')
            return

        # stop task
        task = self._tasks[key]
        self._progress.stop_task(task)
        self._progress.remove_task(task)

        # update log
        if success:
            self._console.log(f'[green]{key} Success ({message})')
        else:
            self._console.log(f'[red]{key} Error ({message})')

    def on_update_progress(self, key: str, cur_progress: int, max_progress: int|None):
        if key not in self._tasks:
            self._console.log(f'Invalid device: {key}')
            return

        # stop task
        task = self._tasks[key]
        self._progress.stop_task(task)

        # update
        self._progress.update(task, completed=cur_progress, total=max_progress)
