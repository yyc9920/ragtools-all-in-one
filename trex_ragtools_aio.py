import argparse
import sys
import logging
import datetime
import json
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
    setLogHandler(
        file_debug_handler,
        logging.DEBUG,
        debug_formatter,
        DebugFilter())

    logger.addHandler(debug_handler)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.addHandler(file_debug_handler)


def getArgs():
    parser = argparse.ArgumentParser(add_help=False)
    actions = [method for method in dir(Action) if callable(
        getattr(Action, method)) and not method.startswith('_')]
    parser.add_argument(
        '--help',
        action='store_true',
        help="Show this help message")
    parser.add_argument(
        '--json_config',
        type=str,
        help=" : load json configuration instead of typing all of the arguments")
    parser.add_argument(
        '--action',
        type=str,
        help=f" : set the type of action you want.\
        (available actions : {', '.join(actions)})")
    # arguments for parseTestset action
    parser.add_argument('--json_filename', type=str, help=' : json file name')
    parser.add_argument('--csv_filename', type=str, help=' : csv file name')
    parser.add_argument(
        '--basepath',
        type=str,
        help=' : base path of the dataset')
    # arguments for creatTestset action
    parser.add_argument(
        '--gpt_model',
        type=str,
        help=' : model name for the generator LLM')
    parser.add_argument(
        '--dataset_source_dir',
        type=str,
        help=' : directory path containing the Markdown files for the dataset')
    parser.add_argument(
        '--testset_test_size',
        type=int,
        help=' : size of the test set')
    parser.add_argument(
        '--testset_comparative_query_ratio',
        type=float,
        help=' : ratio of comparative query examples in the test set')
    parser.add_argument(
        '--testset_specific_query_ratio',
        type=float,
        help=' : ratio ofspecific query examples in the test set')
    parser.add_argument(
        '--testset_filename',
        type=str,
        help=' : path to save the generated test set')
    # arguments for evaluateTestset action
    parser.add_argument(
        '--eval_result_filename',
        type=str,
        help=' : path to save the generated evaluation result')
    parser.add_argument(
        '--eval_metrics',
        type=list,
        help=' : list of evaluation metrics')
    parser.add_argument(
        '--eval_iterations',
        type=int,
        help=' : number of evaluation iterations')
    printHelpMessageForEachAction(parser)
    args = parser.parse_args()

    if args.json_config:
        # Load JSON config file
        if Path(args.json_config).exists():
            with open(args.json_config, 'r') as json_file:
                json_args = json.load(json_file)
                # Update the parser with the JSON config
                for key, value in json_args.items():
                    if f"--{key}" in parser._option_string_actions:
                        setattr(args, key, value)
                    else:
                        print(f"Warning: '{key}' is not a valid argument and will be ignored.")
        else:
            print(f"Error: JSON file '{args.json_config}' does not exist.")

    return args


def printHelpMessageForEachAction(parser):
    args, unknown_args = parser.parse_known_args()
    if args.help:
        if args.action:
            try:
                print(
                    "\n" +
                    args.action +
                    "\n" +
                    getattr(Action, args.action).__doc__)
            except BaseException:
                print(f"Error: Unknown Action '{args.action}'")
        else:
            # Default help message when no option or unrecognized option is
            # provided
            parser.print_help()
        sys.exit()


def checkValidateArgs(args):
    validate_args = {
        "parseTestset": {
            "arguments": [
                args.json_filename,
                args.csv_filename,
                args.eval_metrics],
            "path_validation_candidates": [args.json_filename]
        },
        "createTestset": {
            "arguments": [
                args.gpt_model,
                args.dataset_source_dir,
                args.testset_test_size,
                args.testset_comparative_query_ratio,
                args.testset_specific_query_ratio,
                args.testset_filename],
            "path_validation_candidates": [args.dataset_source_dir]
        },
        "generateContext": {
            "arguments": [
                args.json_filename,
                args.testset_filename],
            "path_validation_candidates": [args.json_filename]
        },
        "evaluateTestset": {
            "arguments": [
                args.json_filename,
                args.eval_result_filename,
                args.eval_iterations,
                args.eval_metrics],
            "path_validation_candidates": [args.json_filename]
        }
    }

    if args.action not in validate_args:
        logger.error(f"Invalid action. Please choose from {', '.join(validate_args.keys())}")
        return False

    if all(validate_args[args.action]["arguments"]):
        if all([Path(path).exists()
               for path in validate_args[args.action]["path_validation_candidates"]]):
            return True
        else:
            logger.error("Invalid path. Please check the path below.")
            logger.error(f"{validate_args[args.action]['path_validation_candidates']}")
            return False
    else:
        logger.error(f"Invalid arguments. Please check mandatory arguments.")
        return False


def main(argv, args):
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    setLogger(logger)
    logger.debug(args)
    if checkValidateArgs(args):
        pass
    else:
        exit(1)

    getattr(Action(logger), args.action)(args)


if __name__ == '__main__':
    argv = sys.argv
    args = getArgs()
    main(argv, args)
