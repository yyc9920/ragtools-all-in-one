import json
from dotenv import load_dotenv
from actions.parse_testset import *
from actions.ragas_testset_creator import RagasTestsetCreator
from actions.ragas_context_generator import generateRagasContextAndAnswers
from actions.ragas_evaluation import RagasEvaluationTestset
import nest_asyncio

nest_asyncio.apply()

load_dotenv()


class Action:
    def __init__(self, logger):
        self.logger = logger

    def evaluateTestset(self, args):
        """
        Evaluates the performance of a GPT model on a given testset.
        evaluation metrics : LLMContextRecall, FactualCorrectness, Faithfulness, SemanticSimilarity
        about ragas metrics : https://docs.ragas.io/en/v0.2.2/concepts/metrics/available_metrics/

        Parameters:
        args (argparse.Namespace): An object containing command-line arguments.
            - args.json_filename (str): The path to the input JSON file containing the testset.
            - args.gpt_model (str): The name of the GPT model to be evaluated.
            - args.eval_result_filename (str): The path to save the generated evaluation result.

        Returns:
        None
        """
        ragasEval = RagasEvaluationTestset(self.logger)
        eval_results = ragasEval.evaluateTestset(args.json_filename, args.gpt_model)
        ragasEval.saveEvaluationResult(eval_results, args.eval_result_filename)

    def generateContext(self, args):
        """
        This function generates context for Ragas using a JSON file containing testset and saves it to a file.

        Parameters:
        args (argparse.Namespace): An object containing command-line arguments.
            - args.json_filename (str): The path to the input JSON file containing the testset.
            - args.testset_filename (str): The path to save the generated context file.

        Returns:
        None
        """
        generateRagasContextAndAnswers(args.json_filename, args.testset_filename, self.logger)

    def createTestset(self, args):
        """
        This function generates a test set using the LangChain library and saves it to a file.

        Parameters:
        args (argparse.Namespace): An object containing command-line arguments.
            - args.gpt_model (str): The model name for the generator LLM.
            - args.dataset_source_dir (str): The directory path containing the Markdown files for the dataset.
            - args.testset_test_size (int): The size of the test set.
            - args.testset_comparative_query_ratio(float): The ratio of comparative query examples in the test set.
            - args.testset_specific_query_ratio(float): The ratio ofspecific query examples in the test set.
            - args.testset_filename (str): The path to save the generated test set.

        Returns:
        None
        """
        ragasTestsetCreator = RagasTestsetCreator(self.logger)
        ragasTestsetCreator.main(args.dataset_source_dir,
             args.testset_test_size,
             args.testset_comparative_query_ratio,
             args.testset_specific_query_ratio,
             args.gpt_model,
             args.testset_filename)

    def parseTestset(self, args):
        """
        Parses a JSON file containing a testset and saves it as a CSV file.

        Parameters:
        args (argparse.Namespace): An object containing command-line arguments.
            - args.json_filename (str): The path to the input JSON file.
            - args.basepath (str): The base path for modifying metadata.
            - args.csv_filename (str): The path to save the output CSV file.

        Returns:
        None
        """
        with open(args.json_filename, 'rt', encoding='UTF8') as file:
            testset = json.load(file)
        testset_without_invalid_gt = removeInvalidGroundTruths(testset)
        testset_parsed = modifyMetadata(testset_without_invalid_gt, args.basepath)
        saveDictToCsv(testset_parsed, args.csv_filename)
        self.logger.info(f"Parsed testset saved as csv in {args.csv_filename}")
