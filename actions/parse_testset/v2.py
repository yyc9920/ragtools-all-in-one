import json
import csv
import re

def convertMetrics(metrics):
    converted_metrics = []
    for metric in metrics:
        if metric is "LLMContextRecall":
            converted_metrics.append("context_recall")
        else:
            metric = re.sub(r'(?<!^)(?=[A-Z])', '_', metric).lower()
            converted_metrics.append(metric)

    return converted_metrics


def main(json_file_path, filename, metrics, logger):
    with open(json_file_path, "r") as f:
        data = json.load(f)

    converted_metrics = convertMetrics(metrics)
    csv_data = []
    header = [
        "index", "user_input", "retrieved_contexts", 
        "response", "reference"
    ]
    header.extend(converted_metrics)
    csv_data.append(header)

    # Populate CSV data
    for index in range(len(data["user_input"])):
        row = [
            index,
            data["user_input"][str(index)],
            "; ".join(data["retrieved_contexts"][str(index)]),  # Join list to string
            data["response"][str(index)],
            data["reference"][str(index)]
        ]
        row.extend([data[metric][str(index)] for metric in converted_metrics])
        csv_data.append(row)

    # Write to CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    logger.info(f"Data has been converted and saved to {filename}")