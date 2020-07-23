import sys
import logging
import os

from nebixbot import log


def get_log_fname_path(filename):
    """Return log dir path"""
    filename = filename.replace(' ', '_')
    log_dir = log.__file__.replace('__init__.py', '')
    return os.path.join(log_dir, f'logfiles/{filename}.log')


def get_file_name(name, version):
    """Return filename"""
    name = name.replace(' ', '_')
    version = version.replace(' ', '_')
    return f'{name}_{version}'


def create_logger(name, filename):
    """Create a logger with console and file handlers"""
    name = name.replace(' ', '_')
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # file handler:
    filename = filename.replace(' ', '_')
    log_fname = get_log_fname_path(filename)
    fh = logging.FileHandler(log_fname, mode='a')
    fh.setLevel(logging.DEBUG)

    # console handler:
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.ERROR)

    # formatter:
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][%(name)s]: "%(message)s"' +
        ' (%(filename)s:%(lineno)s)', datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def delete_log_file(filename):
    """Delete log file from log dir"""
    filename = filename.replace(' ', '_')
    log_fname = get_log_fname_path(filename)
    if os.path.isfile(log_fname):
        os.remove(log_fname)
        return True
    else:
        return False
