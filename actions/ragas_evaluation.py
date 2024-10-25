from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity
from ragas import evaluate
from ragas import EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
import json


class RagasEvaluationTestset:
    def __init__(self, logger):
        self.logger = logger

    def evaluateTestset(self, json_file_path, model):
        with open(json_file_path, "r") as f:
            json_data = json.load(f)
        eval_dataset = EvaluationDataset.from_dict(json_data["samples"])
        evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=model))
        metrics = [LLMContextRecall(), FactualCorrectness(), Faithfulness(), SemanticSimilarity()]
        metrics_names = [m.name for m in metrics]
        self.logger.info("Start ragas evaluation with metrics below :")
        self.logger.info(f"{metrics_names}")
        results = evaluate(dataset=eval_dataset, metrics=metrics, llm=evaluator_llm,)
        self.logger.info("ragas evaluation Complete!!")
        self.logger.info("Scores :")
        self.logger.info(results.scores)

        return results

    def saveEvaluationResult(self, eval_result, file_path):
        if file_path is None:
            return False

        if not file_path.endswith(".json"):
            file_path += ".json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(eval_result.to_pandas().to_dict(), f, indent=4)
        self.logger.info(f"Save to json file : {file_path}")
