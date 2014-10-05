from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
import logging
import os
import sys


class SynchronousRotatingFileHandler(RotatingFileHandler):

    def flush(self):
        RotatingFileHandler.flush(self)
        if hasattr(self.stream, 'fileno') and hasattr(os, 'fsync'):
            fd = self.stream.fileno()
            os.fsync(fd)


class LoggingConfigurator(object):

    def __init__(self, level="INFO",
                       num_log_files=3,
                       file_size=100000,
                       file_path=".",
                       file_name="log.txt",
                       format="%(asctime)s | %(name)-12s | %(message)s",
                       date_format="%m/%d %H:%M:%S",
                       log_levels=None):
        self.level = level
        self.num_log_files = num_log_files
        self.file_size = file_size
        self.file_path = file_path
        self.file_name = file_name
        self.format = format
        self.date_format = date_format
        self.log_levels = log_levels

    def start(self):

        # Here we subtract one from num_log_files because for the
        # RotatingFileHandler the argument taken is the maximum number appended
        # to the end of the fall name.  Since there is an original the total
        # number of log files will be one plus what is passed in
        logfilename = os.path.join(self.file_path, self.file_name)
        fh = SynchronousRotatingFileHandler(filename=logfilename,
                                            maxBytes=self.file_size,
                                            backupCount=self.num_log_files - 1)
        stream_handler = StreamHandler(sys.stdout)

        logger = logging.getLogger("")
        logger.setLevel(self._parse_level(self.level))
        for handler in logger.handlers:
            logger.removeHandler(handler)

        logger.addHandler(fh)
        logger.addHandler(stream_handler)
        formatter = Formatter(self.format, self.date_format)
        fh.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        if self.log_levels is not None:
            for name, level in self.log_levels.iteritems():
                logging.getLogger(name).setLevel(self._parse_level(level))

    def _parse_level(self, level):
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