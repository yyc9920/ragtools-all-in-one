# Ragtools All In One

import argparse
import sys
import logging
import datetime
from pathlib import Path
from action import Action


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
    Path("./log").mkdir(parents=True, exist_ok=True)
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
    parser.add_argument('-action', help=' : set the type of action you want')
    parser.add_argument('-json_filename', help=' : json file name')
    parser.add_argument('-csv_filename', help=' : csv file name')
    parser.add_argument('-basepath', help=' : base path of the dataset')
    args = parser.parse_args()
    return args


def checkArgsValidation(args):
    validate_args = {
        "parseTestset" : {
            "arguments" : [args.json_filename, args.csv_filename, args.basepath],
            "path_validation_candidate" : [args.json_filename]
        }
    }

    if args.action not in validate_args:
        logger.error(f"Invalid action. Please choose from {', '.join(validate_args.keys())}")
        return False

    if all(validate_args[args.action]["arguments"]):
        logger.error(f"Invalid arguments. Please check mandatory arguments.")
        if all([Path(args.json_filename).exists() for path in validate_args[args.action]["path_validation_candidate"]]):
            return True
        else:
            logger.error(f"Invalid path. Please check the path below.\n{validate_args[args.action]['path_validation_candidate']}")
            return False
    else:
        return False


def main(argv, args):
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    setLogger(logger)
    action = Action(logger)

    if checkArgsValidation(args):
        pass
    else:
        exit(1)

    getattr(action, args.action)(args)


if __name__ == '__main__':
    argv = sys.argv
    args = getArgs()
    main(argv, args)
