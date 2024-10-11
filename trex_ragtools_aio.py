# Ragtools All In One

import argparse
import sys
import logging
import datetime
import pathlib


def getLogger():
    pathlib.Path("./log").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s [%(filename)s %(lineno)d] [%(levelname)s] : %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    now = datetime.datetime.now().strftime('%m-%d-%Y_%H_%M_%S')
    file_handler = logging.FileHandler(f"./log/{now}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-name', help=' : Please set the name')
    parser.add_argument('-option', help=' : train or prediction', default='train')
    args = parser.parse_args()

    return args


def main(argv, args):
    logger = getLogger()
    logger.info(f'argv : {argv}')
    logger.info(f'args : {args}')


if __name__ == '__main__':
    argv = sys.argv
    args = getArgs()
    main(argv, args)
