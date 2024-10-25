from trex_ai_chatbot_tools import text_gen as tg
from ragas import EvaluationDataset
import json
import logging

logger = logging.getLogger(__name__)


def generateRagasContextAndAnswers(json_file_path, save_file_path):
    # JSON 파일 읽기
    with open(json_file_path, "r") as f:
        json_data = json.load(f)

    evaluation_dataset = EvaluationDataset.from_dict(json_data["samples"])
    evaluation_dataset_dict = evaluation_dataset.dict()
    print(f"evaluation_dataset : {evaluation_dataset_dict}")

    for i, obj in enumerate(evaluation_dataset_dict["samples"]):
        print(f"\rGenerating RAGAS json...({i+1}/{len(evaluation_dataset_dict['samples'])})")
        response = tg.answer_question(obj["user_input"])
        obj.update({"retrieved_contexts": response["list"], "response": response["response"]})

    # JSON 파일 저장
    with open(save_file_path, "w") as f:
        json.dump(evaluation_dataset_dict, f, indent=4)
        print(f"Save to json file : {save_file_path}")


if __name__ == "__main__":
    basepath = "/home/kendrick/workspace/project/ai_application/rag/source/ragas_evaluation/241018_embedding_dataset"
    path = f"{basepath}/testset_241018.json"
    savefilepath = f"{basepath}/testset_241018_with_contexts.json"
    generateRagasContextAndAnswers(path, savefilepath)
