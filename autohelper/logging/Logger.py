import logging
import os
import traceback
from logging.handlers import TimedRotatingFileHandler

from autohelper.gui.Communicate import communicate
from autohelper.util.path import get_path_relative_to_exe, ensure_dir_for_file


class CommunicateHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        log_message = self.format(record)
        communicate.log.emit(record.levelno, log_message)


formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s %(message)s')
communicate_handler = CommunicateHandler()
communicate_handler.setFormatter(formatter)


def get_substring_from_last_dot_exclusive(s):
    # Find the last occurrence of "."
    last_dot_index = s.rfind(".")
    # If there's no ".", return an empty string or the original string based on your need
    if last_dot_index == -1:
        return ""  # or return s to return the whole string if there's no dot
    # Slice the string from just after the last "." to the end
    return s[last_dot_index + 1:]


auto_helper_logger = logging.getLogger("autohelper")


def config_logger(config):
    if config.get('debug'):
        auto_helper_logger.setLevel(logging.DEBUG)
    else:
        auto_helper_logger.setLevel(logging.INFO)

    auto_helper_logger.handlers = []
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    auto_helper_logger.addHandler(console_handler)
    auto_helper_logger.addHandler(communicate_handler)
    logging.getLogger().handlers = []

    if config.get('log_file'):
        logger_file = get_path_relative_to_exe(config.get('log_file'))
        ensure_dir_for_file(logger_file)

        os.makedirs("logs", exist_ok=True)
        # File handler with rotation
        file_handler = TimedRotatingFileHandler(logger_file, when="midnight", interval=1,
                                                backupCount=7, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # File handler level
        auto_helper_logger.addHandler(file_handler)

    if config.get('error_log_file'):
        error_log_file = get_path_relative_to_exe(config.get('error_log_file'))
        ensure_dir_for_file(error_log_file)

        os.makedirs("logs", exist_ok=True)
        # File handler with rotation
        file_handler = TimedRotatingFileHandler(error_log_file, when="midnight", interval=1,
                                                backupCount=7, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.ERROR)  # File handler level
        auto_helper_logger.addHandler(file_handler)


class Logger:
    def __init__(self, name):
        # Initialize the logger with the name of the subclass
        self.logger = auto_helper_logger
        self.name = name

    def debug(self, message):
        self.logger.debug(f"{self.name}:{message}")

    def info(self, message):
        self.logger.info(f"{self.name}:{message}")

    def warning(self, message):
        self.logger.warning(f"{self.name}:{message}")

    def error(self, message, exception=None):
        if exception is not None:
            traceback.print_exc()
            stack_trace_str = traceback.format_exc()
        else:
            stack_trace_str = ""
        self.logger.error(f"{self.name}:{message} {stack_trace_str}")

    def critical(self, message):
        self.logger.critical(f"{self.name}:{message}")


def get_logger(name):
    return Logger(name)
