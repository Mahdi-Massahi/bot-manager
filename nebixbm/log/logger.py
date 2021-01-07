import sys
import logging
from logging.handlers import RotatingFileHandler
import os
from colorlog import ColoredFormatter
import shutil
import datetime

from nebixbm import log


LOGFILES_DIR = "logfiles/"


def get_log_fname_path(filename):
    """Return log dir path"""
    filename = filename.replace(" ", "_")
    log_dir = log.__file__.replace("__init__.py", "")
    return os.path.join(log_dir, f"{LOGFILES_DIR}{filename}.log")


def get_file_name(name, version):
    """Return filename"""
    name = name.replace(" ", "_")
    if version:
        version = version.replace(" ", "_")
        return f"{name}_{version}"
    else:
        return f"{name}"


def create_logger(name, filename):
    """Create a logger with console and file handlers"""
    name = name.replace(" ", "_")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    filename = filename.replace(" ", "_")
    log_fname = get_log_fname_path(filename)

    # file handler:
    if not logger.handlers:
        # rotating file handler:
        fh = RotatingFileHandler(
            log_fname,
            maxBytes=24_000_000,
            backupCount=100
        )
        fh.setLevel(logging.DEBUG)

        # console handler:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(logging.DEBUG)

        # formatter:
        formatter = ColoredFormatter(
            "[%(asctime)s.%(msecs)03d]"
            + "[%(log_color)s%(levelname)s%(reset)s]"
            + '[%(name)s]: "%(log_color)s%(message)s%(reset)s"'
            + " (%(filename)s:%(lineno)s)",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger, log_fname


def delete_log_file(filename):
    """Delete log file from log dir"""
    filename = filename.replace(" ", "_")
    log_fname = get_log_fname_path(filename)
    if os.path.isfile(log_fname):
        os.remove(log_fname)
        return True
    else:
        return False


def delete_all_logs() -> bool:
    """Deletes all logfiles"""
    log_dir = log.__file__.replace("__init__.py", "")
    logsfile_dir = os.path.join(log_dir, LOGFILES_DIR)
    try:
        for filename in os.listdir(logsfile_dir):
            file_path = os.path.join(logsfile_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                if file_path.endswith(".log") or file_path.endswith(".csv"):
                    os.unlink(file_path)
        return True
    except Exception as err:
        print(f"Failed to delete {file_path}: {err}")
        return False


def get_logs_dir():
    """Return logfiles directory"""
    log_dir = log.__file__.replace("__init__.py", "")
    logsfile_dir = os.path.join(log_dir, LOGFILES_DIR)
    return logsfile_dir


def zip_existing_logfiles():
    """Zips 'logfile' dir and returns the zipfile path"""
    dt = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    zipfile_path = shutil.make_archive(f"logs_{dt}", 'zip', get_logs_dir())
    return zipfile_path
