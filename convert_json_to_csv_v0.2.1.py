import json
import os
import csv

def main(json_file_path):
    with open(json_file_path, "r") as f:
        data = json.load(f)

    csv_data = []
    header = [
        "index", "user_input", "retrieved_contexts", 
        "response", "reference", "context_recall", "factual_correctness",
        "faithfulness", "semantic_similarity"
    ]
    csv_data.append(header)

    # Populate CSV data
    for index in range(len(data["user_input"])):
        row = [
            index,
            data["user_input"][str(index)],
            "; ".join(data["retrieved_contexts"][str(index)]),  # Join list to string
            data["response"][str(index)],
            data["reference"][str(index)],
            data["context_recall"][str(index)],
            data["factual_correctness"][str(index)],
            data["faithfulness"][str(index)],
            data["semantic_similarity"][str(index)]
        ]
        csv_data.append(row)

    # Write to CSV file
    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    print("Data has been written to output.csv")

main(".\\eval_result_241018.json")