from __future__ import annotations
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

from utils.debug import get_logger

log = get_logger(__name__)


class ShaderReloader(FileSystemEventHandler):
    def __init__(self, paths: list[Path], callback):
        self.paths = [p.resolve() for p in paths]
        self.callback = callback

    def on_modified(self, event):
        for p in self.paths:
            if event.src_path.startswith(str(p)):
                log.debug("File modified: %s", event.src_path)
                self.callback()
                break


def watch(paths: list[Path], callback):
    log.debug("Starting watch on paths: %s", paths)
    event_handler = ShaderReloader(paths, callback)
    observer = Observer()
    for p in paths:
        observer.schedule(event_handler, str(p), recursive=True)
    observer.start()
    return observer
