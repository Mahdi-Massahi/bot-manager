import sys
import logging
import os

from nebixbm import log
from nebixbm.other.tcolors import Tcolors


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
        fh = logging.FileHandler(log_fname, mode="a")
        fh.setLevel(logging.DEBUG)

        # console handler:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setLevel(logging.DEBUG)

        # formatter:
        formatter = logging.Formatter(
            f"[%(asctime)s][{Tcolors.OKBLUE}%(levelname)s{Tcolors.ENDC}]"
            + '[%(name)s]: "%(message)s"'
            + " (%(filename)s:%(lineno)s)",
            datefmt="%Y-%m-%d %H:%M:%S",
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
                if file_path.endswith(".log"):
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
