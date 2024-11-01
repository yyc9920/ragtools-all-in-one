import json
from dotenv import load_dotenv

load_dotenv()


class Action:
    def __init__(self, logger):
        self.logger = logger

    def evaluateTestset(self, args):
        """
        Evaluates the performance of a GPT model on a given testset.
        evaluation metrics : LLMContextRecall, FactualCorrectness, Faithfulness, SemanticSimilarity
        about ragas metrics : https://docs.ragas.io/en/v0.2.2/concepts/metrics/available_metrics/

        Arguments:
            --json_filename (str): The path to the input JSON file containing the testset.
            --gpt_model (str): The name of the GPT model to be evaluated.
            --eval_result_filename (str): The path to save the generated evaluation result.
            --eval_iterations (int): Number of evaluation iterations
        """
        from actions.ragas_evaluation import RagasEvaluationTestset
        ragasEval = RagasEvaluationTestset(self.logger)

        scores_store = []
        summed_scores = []
        for _ in range(args.eval_iterations):
            self.logger.info(f"Evaluating... (iter {i+1}/{args.eval_iterations})")
            eval_results = ragasEval.evaluateTestset(
                args.json_filename, args.gpt_model)
            scores_store.append(eval_results.scores)

        for i in range(len(scores_store[0])):
            total = {
                'context_recall': 0,
                'factual_correctness': 0,
                'faithfulness': 0,
                'semantic_similarity': 0
            }
            
            # Sum the scores from each list
            for score in scores_store:
                total['context_recall'] += score[i]['context_recall']
                total['factual_correctness'] += score[i]['factual_correctness']
                total['faithfulness'] += score[i]['faithfulness']
                total['semantic_similarity'] += score[i]['semantic_similarity']
            
            # Calculate the average
            average = {
                'context_recall': total['context_recall'] / len(scores_store),
                'factual_correctness': total['factual_correctness'] / len(scores_store),
                'faithfulness': total['faithfulness'] / len(scores_store),
                'semantic_similarity': total['semantic_similarity'] / len(scores_store)
            }
            
            summed_scores.append(average)

        eval_results.scores = summed_scores
        self.logger.info("Summed Scores :")
        self.logger.info(summed_scores)
        ragasEval.saveEvaluationResult(eval_results, args.eval_result_filename)

    def generateContext(self, args):
        """
        This function generates context for Ragas using a JSON file containing testset and saves it to a file.

        Arguments:
            --json_filename (str): The path to the input JSON file containing the testset.
            --testset_filename (str): The path to save the generated context file.
        """
        from actions.ragas_context_generator import generateRagasContextAndAnswers
        generateRagasContextAndAnswers(
            args.json_filename,
            args.testset_filename,
            self.logger)

    def createTestset(self, args):
        """
        This function generates a test set using the LangChain library and saves it to a file.

        Arguments:
            --gpt_model (str): The model name for the generator LLM.
            --dataset_source_dir (str): The directory path containing the Markdown files for the dataset.
            --testset_test_size (int): The size of the test set.
            --testset_comparative_query_ratio(float): The ratio of comparative query examples in the test set.
            --testset_specific_query_ratio(float): The ratio ofspecific query examples in the test set.
            --testset_filename (str): The path to save the generated test set.
        """
        from actions.ragas_testset_creator import RagasTestsetCreator
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

        Arguments:
            --json_filename (str): The path to the input JSON file.
            --basepath (str): The base path for modifying metadata.
            --csv_filename (str): The path to save the output CSV file.
        """
        from actions.parse_testset import removeInvalidGroundTruths, modifyMetadata, saveDictToCsv
        with open(args.json_filename, 'rt', encoding='UTF8') as file:
            testset = json.load(file)
        testset_without_invalid_gt = removeInvalidGroundTruths(testset)
        testset_parsed = modifyMetadata(
            testset_without_invalid_gt, args.basepath)
        saveDictToCsv(testset_parsed, args.csv_filename)
        self.logger.info(f"Parsed testset saved as csv in {args.csv_filename}")
