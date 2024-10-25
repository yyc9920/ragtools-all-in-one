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
    parser = argparse.ArgumentParser(add_help=False)
    actions = [method for method in dir(Action) if callable(getattr(Action, method)) and not method.startswith('_')]
    parser.add_argument('--help', action='store_true', help="Show this help message")
    parser.add_argument('--action', type=str, required=True, help=f" : set the type of action you want.\
        (available actions : {', '.join(actions)})")
    # arguments for parseTestset action
    parser.add_argument('--json_filename', type=str, help=' : json file name')
    parser.add_argument('--csv_filename', type=str, help=' : csv file name')
    parser.add_argument('--basepath', type=str, help=' : base path of the dataset')
    # arguments for creatTestset action
    parser.add_argument('--gpt_model', type=str, help=' : model name for the generator LLM')
    parser.add_argument('--dataset_source_dir', type=str, help=' : directory path containing the Markdown files for the dataset')
    parser.add_argument('--testset_test_size', type=int, help=' : size of the test set')
    parser.add_argument('--testset_comparative_query_ratio', type=float, help=' : ratio of comparative query examples in the test set')
    parser.add_argument('--testset_specific_query_ratio', type=float, help=' : ratio ofspecific query examples in the test set')
    parser.add_argument('--testset_filename', type=str, help=' : path to save the generated test set')
    printHelpMessageForEachAction(parser)
    args = parser.parse_args()
    return args


def printHelpMessageForEachAction(parser):
    args, unknown_args = parser.parse_known_args()
    if args.help:
        if args.action == 'createTestset':
            print("""
createTestset

    This action generates a test set using the LangChain library and saves it to a file.

    arguments:
        --gpt_model (str): The model name for the generator LLM.
        --dataset_source_dir (str): The directory path containing the Markdown files for the dataset.
        --testset_test_size (int): The size of the test set.
        --testset_comparative_query_ratio (float): The ratio of comparative query examples in the test set.
        --testset_specific_query_ratio (float): The ratio of specific query examples in the test set.
        --testset_filename (str): The path to save the generated test set.
            """)
        elif args.action == 'parseTestset':
            print("""
parseTestset

    Parses a JSON file containing a testset and saves it as a CSV file.

    arguments:
        --json_filename (str): The path to the input JSON file.
        --basepath (str): The base path for modifying metadata.
        --csv_filename (str): The path to save the output CSV file.
            """)
        elif args.action == 'generateContext':
            print("""
generateContext

    Generates context for Ragas using a JSON file containing testset and saves it to a file.

    arguments:
        --json_filename (str): The path to the input JSON file containing the testset.
        --testset_filename (str): The path to save the generated context file.
            """)
        else:
            # Default help message when no option or unrecognized option is provided
            parser.print_help()
        sys.exit()


def checkValidateArgs(args):
    validate_args = {
        "parseTestset" : {
            "arguments" : [
                args.json_filename,
                args.csv_filename,
                args.basepath],
            "path_validation_candidates" : [args.json_filename]
        },
        "createTestset" : {
            "arguments" : [
                args.gpt_model,
                args.dataset_source_dir,
                args.testset_test_size,
                args.testset_comparative_query_ratio,
                args.testset_specific_query_ratio,
                args.testset_filename],
            "path_validation_candidates" : [args.dataset_source_dir]
        },
        "generateContext" : {
            "arguments" : [
                args.json_filename,
                args.testset_filename],
            "path_validation_candidates" : [args.json_filename]
        }
    }

    if args.action not in validate_args:
        logger.error(f"Invalid action. Please choose from {', '.join(validate_args.keys())}")
        return False

    if all(validate_args[args.action]["arguments"]):
        if all([Path(path).exists() for path in validate_args[args.action]["path_validation_candidates"]]):
            return True
        else:
            logger.error(f"Invalid path. Please check the path below.\n{validate_args[args.action]['path_validation_candidates']}")
            return False
    else:
        logger.error(f"Invalid arguments. Please check mandatory arguments.")
        return False


def main(argv, args):
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    setLogger(logger)
    action = Action(logger)

    logger.debug(args)

    if checkValidateArgs(args):
        pass
    else:
        exit(1)

    getattr(action, args.action)(args)


if __name__ == '__main__':
    argv = sys.argv
    args = getArgs()
    main(argv, args)
