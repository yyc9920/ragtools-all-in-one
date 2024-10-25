from trex_ai_chatbot_tools import text_gen as tg
from ragas import EvaluationDataset
import json


def generateRagasContextAndAnswers(json_file_path, save_file_path, logger):
    # JSON 파일 읽기
    with open(json_file_path, "r") as f:
        json_data = json.load(f)

    evaluation_dataset = EvaluationDataset.from_dict(json_data["samples"])
    evaluation_dataset_dict = evaluation_dataset.dict()

    for i, obj in enumerate(evaluation_dataset_dict["samples"]):
        logger.info(f"Generating RAGAS json...({i+1}/{len(evaluation_dataset_dict['samples'])})")
        response = tg.answer_question(obj["user_input"])
        obj.update({"retrieved_contexts": response["list"], "response": response["response"]})

    # JSON 파일 저장
    with open(save_file_path, "w") as f:
        json.dump(evaluation_dataset_dict, f, indent=4)
        logger.info(f"Save to json file : {save_file_path}")
