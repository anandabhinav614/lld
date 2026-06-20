from enum import IntEnum
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import json
import sys
from threading import Lock
from datetime import datetime, timezone
from threading import current_thread
from typing import Iterable, Tuple


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    FATAL = 50

@dataclass(frozen=True)
class LogRecord:
    timestamp: datetime
    level: LogLevel
    message: str
    thread_name: str

class Formatter(ABC):
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        pass

class PlainTextFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        timestamp = record.timestamp.isoformat()
        return f"{timestamp} [{record.level.name}] [{record.thread_name}] {record.message}"
    
class JsonFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        return json.dumps({
            "timestamp": record.timestamp.isoformat(),
            "level": record.level.name,
            "thread": record.thread_name,
            "message": record.message,
        })

class Sink(ABC):
    @abstractmethod
    def write(self, formatted: str) -> None:
        pass

class ConsoleSink(Sink):
    def write(self, formatted: str) -> None:
        print(formatted)

class FileSink(Sink):
    def __init__(self, file_path: str):
        self._file = open(file_path, "a", encoding="utf-8")

    def write(self, formatted: str) -> None:
        self._file.write(formatted + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()

class Destination:
    def __init__(self, formatter: Formatter, min_level: LogLevel, sink: Sink):
        self._formatter = formatter
        self._min_level = min_level
        self._sink = sink
        self._lock = Lock()

    def write(self, record: LogRecord) -> None:
        if record.level < self._min_level:
            return

        formatted = self._formatter.format(record)

        with self._lock:
            try:
                self._sink.write(formatted)
            except Exception as exc:
                sys.stderr.write(f"logger: sink write failed: {exc}\n")

class Logger:
    def __init__(self, destinations: Iterable[Destination]):
        self._destinations: Tuple[Destination, ...] = tuple(destinations)

    def log(self, level: LogLevel, message: str) -> None:
        record = LogRecord(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            thread_name=current_thread().name,
        )

        for destination in self._destinations:
            destination.write(record)

    def debug(self, message: str) -> None:
        self.log(LogLevel.DEBUG, message)

    def info(self, message: str) -> None:
        self.log(LogLevel.INFO, message)

    def warn(self, message: str) -> None:
        self.log(LogLevel.WARN, message)

    def error(self, message: str) -> None:
        self.log(LogLevel.ERROR, message)

    def fatal(self, message: str) -> None:
        self.log(LogLevel.FATAL, message)
