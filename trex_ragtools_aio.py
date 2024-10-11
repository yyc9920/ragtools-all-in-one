# Ragtools All In One

import argparse
import sys
import logging
import datetime
import pathlib


def setLogHandler(log_handler, level, formatter, log_filter=None):
    handler = log_handler
    handler.setLevel(level)
    if log_filter is not None:
        handler.addFilter(log_filter)
    handler.setFormatter(formatter)


def setLogger(logger):
    date_format = '%H:%M:%S'
    default_formatter = logging.Formatter(
        '%(asctime)s [%(module)s %(lineno)d] [%(levelname)s] : %(message)s',
        datefmt=date_format)
    debug_formatter = logging.Formatter(
        '%(asctime)s [%(module)s %(funcName)s %(lineno)d] [%(levelname)s] : %(message)s',
        datefmt=date_format)

    class DebugFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.DEBUG

    debug_handler = logging.StreamHandler()
    stream_handler = logging.StreamHandler()
    setLogHandler(debug_handler, logging.DEBUG, debug_formatter, DebugFilter())
    setLogHandler(stream_handler, logging.INFO, default_formatter)

    now = datetime.datetime.now().strftime('%m-%d-%Y_%H_%M_%S')
    pathlib.Path("./log").mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(f"./log/{now}.log")
    file_debug_handler = logging.FileHandler(f"./log/{now}.log")
    setLogHandler(file_handler, logging.INFO, default_formatter)
    setLogHandler(file_debug_handler, logging.DEBUG, debug_formatter, DebugFilter())

    logger.addHandler(debug_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.addHandler(file_debug_handler)


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-name', help=' : Please set the name')
    parser.add_argument('-option', help=' : train or prediction', default='train')
    args = parser.parse_args()
    return args


def main(argv, args):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    setLogger(logger)
    logger.info(f'argv : {argv}')
    logger.info(f'args : {args}')
    logger.debug("test")
    logger.warning("test")


if __name__ == '__main__':
    argv = sys.argv
    args = getArgs()
    main(argv, args)
