from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
import paths
import logging
import os
import sys


def _parse_level(level):
    level = level.upper()
    levels = {"NOTSET": logging.NOTSET,
              "DEBUG": logging.DEBUG,
              "INFO": logging.INFO,
              "WARN": logging.WARN,
              "ERROR": logging.ERROR,
              "CRITICAL": logging.CRITICAL}

    if level in levels:
        return levels[level]
    else:
        raise KeyError("Logging level \"%s\" does not exist" % level)


class _SynchronousRotatingFileHandler(RotatingFileHandler):
    def flush(self):
        RotatingFileHandler.flush(self)
        if hasattr(self.stream, 'fileno') and hasattr(os, 'fsync'):
            fd = self.stream.fileno()
            os.fsync(fd)


def configure(level="INFO",
              num_log_files=3,
              file_size=100000,
              file_path=".",
              file_name="log.txt",
              log_format="%(asctime)s | %(name)-12s | %(message)s",
              date_format="%m/%d %H:%M:%S",
              log_levels=None):
    """Configure the global logger"""

    paths.init_dirs(file_path)

    # Here we subtract one from num_log_files because for the
    # RotatingFileHandler the argument taken is the maximum number appended
    # to the end of the fall name.  Since there is an original the total
    # number of log files will be one plus what is passed in
    logfilename = os.path.join(file_path, file_name)
    fh = _SynchronousRotatingFileHandler(filename=logfilename,
                                         maxBytes=file_size,
                                         backupCount=num_log_files - 1)
    stream_handler = StreamHandler(sys.stdout)

    logger = logging.getLogger("")
    logger.setLevel(_parse_level(level))
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.addHandler(fh)
    logger.addHandler(stream_handler)
    formatter = Formatter(log_format, date_format)
    fh.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    if log_levels is not None:
        for name, level in log_levels.iteritems():
            logging.getLogger(name).setLevel(_parse_level(level))
