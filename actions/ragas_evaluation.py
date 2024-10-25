from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity
from ragas import evaluate
from ragas import EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
import json


def evaluateTestset(json_file_path, model):
    with open(json_file_path, "r") as f:
        json_data = json.load(f)
    eval_dataset = EvaluationDataset.from_dict(json_data["samples"])
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=model))
    metrics = [LLMContextRecall(), FactualCorrectness(), Faithfulness(), SemanticSimilarity()]
    results = evaluate(dataset=eval_dataset, metrics=metrics, llm=evaluator_llm,)

    return results


def saveEvaluationResult(eval_result, file_path):
    print(__name__)
    if file_path is None:
        return False

    if not file_path.endswith(".json"):
        file_path += ".json"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(eval_result.to_pandas().to_dict(), f, indent=4)
    print(f"Save to json file : {file_path}")


if __name__ == "__main__":
    json_file = rf"C:\work\project\AI_Application\rag\source\ragtools-all-in-one\sample_with_context.json"
    model = "gpt-4o-mini"

    saveEvaluationResult(evaluateTestset(json_file, model), "evaluation_result.json")
