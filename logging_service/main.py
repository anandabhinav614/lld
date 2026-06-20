from enum import Enum
from abc import ABC, abstractmethod
from datetime import datetime
from threading import Lock

class LogLevel(Enum):
    DEBUG=1
    INFO=2
    WARN=3
    ERROR=4
    FATAL=5

class LogRecord:
    def __init__(self, message,level:LogLevel,timestamp):
        self.message = message
        self.level = level
        self.timestamp = timestamp
        

class Formatter(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def format(self, record:LogRecord):
        pass

class JsonFormatter(Formatter):
    def format(self, record:LogRecord) -> dict:
        return {"log_type":record.level.name,
                "messge":record.message,
                "timestamp":record.timestamp
                }

class TxtFormatter(Formatter):
    def format(self, record:LogRecord) -> str:
       return f"{record.timestamp} {record.level.name} {record.message}"    #2026-06-20 INFO User created


class Destination(ABC):
    def __init__(self, formatter:Formatter, min_level:LogLevel):
        self.formatter = formatter
        self.min_level = min_level
        self.lock = Lock()

    @abstractmethod
    def write(self, record:LogRecord):
        pass
    def is_valid_log(self, log_level:LogLevel):
        return log_level.value>=self.min_level.value

class ConsoleDestination(Destination):
    def __init__(self, formatter:Formatter, min_level:LogLevel):
        super().__init__(formatter, min_level)

    def write(self, record:LogRecord):
        if not self.is_valid_log(record.level):
            return
        output = self.formatter.format(record)
        with self.lock:
            print(output)
        
class FileDestination(Destination):
    def __init__(self, formatter:Formatter, min_level:LogLevel, file_path):
        super().__init__(formatter, min_level)
        self.file_path = file_path
        self.logs = []
        
    def write(self, record:LogRecord):
        if not self.is_valid_log(record.level):
            return
        output = self.formatter.format(record)
        with self.lock:
            self.logs.append(output)    

class Logger:
    def __init__(self, destinations:list[Destination]):
        self.destinations = destinations

    def debug(self, message:str):
        self._create_log_record(message, LogLevel.DEBUG)

    def info(self, message:str):
        self._create_log_record(message, LogLevel.INFO)

    def warn(self, message:str):
        self._create_log_record(message, LogLevel.WARN)

    def error(self, message:str):
        self._create_log_record(message, LogLevel.ERROR)

    def fatal(self, message:str):
        self._create_log_record(message, LogLevel.FATAL)

    def _create_log_record(self, message:str, log_level:LogLevel):
        log_record = LogRecord(message, log_level, datetime.now())
        for dest in self.destinations:
            dest.write(log_record)

def main():
    console = ConsoleDestination(
    formatter=JsonFormatter(),
    min_level=LogLevel.DEBUG
    )

    file = FileDestination(
    file_path="app.log",
    formatter=TxtFormatter(),
    min_level=LogLevel.WARN
    )

    logger = Logger([console, file])


