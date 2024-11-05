# ragtools-all-in-one

all in one rag tools for personal needs

## Setup

### Setup Virtual ENV

```bash
git clone https://github.com/yyc9920/ragtools-all-in-one.git
python -m venv ragtools-all-in-one
cd ragtools-all-in-one

# Mac or linux
source ./bin/activate

# Windows
Scripts\activate

pip install -r requirements
```

### Setup dotenv

Copy `.env_template` to `.env` and fill the env variables.

```
OPENAI_API_KEY=[my_openai_key]
```

### Setup nltk

Run `nltk_download.py` script once for the first time to download nltk tools.

```bash
python nltk_download.py
```

### Setup trex_ai_chatbot_tools

```bash
git clone git@[pangyo_gitlab_server_ip]:exsol/crossroads/phase-1.git
cd phase-1
git checkout embedding_to_gpt
mv trex_ai_chatbot_tools /path/to/python/env/lib/site-packages
```

### Setup embedding DocDB server

This setup must be preceded by the [generateContext](#actions) action.

Download [this](https://dev-aistudio-artifact-bucket.s3.ap-northeast-2.amazonaws.com/DocumentDB+Local+Setup.pdf) guide document and follow the instructions.

## User Guide

### Basic Usage

You can check the full help message like below.

```bash
python trex_ragtools_aio.py --help
usage: trex_ragtools_aio.py [--help] [--json_config JSON_CONFIG] [--action ACTION] [--json_filename JSON_FILENAME] [--csv_filename CSV_FILENAME] [--basepath BASEPATH] [--gpt_model GPT_MODEL]
                            [--dataset_source_dir DATASET_SOURCE_DIR] [--testset_test_size TESTSET_TEST_SIZE] [--testset_comparative_query_ratio TESTSET_COMPARATIVE_QUERY_RATIO]
                            [--testset_specific_query_ratio TESTSET_SPECIFIC_QUERY_RATIO] [--testset_filename TESTSET_FILENAME] [--eval_result_filename EVAL_RESULT_FILENAME] [--eval_metrics EVAL_METRICS]
                            [--eval_iterations EVAL_ITERATIONS]

options:
  --help                Show this help message
  --json_config JSON_CONFIG
                        : load json configuration instead of typing all of the arguments
  --action ACTION       : set the type of action you want. (available actions : createTestset, evaluateTestset, generateContext, parseTestset)
  --json_filename JSON_FILENAME
                        : json file name
  --csv_filename CSV_FILENAME
                        : csv file name
  --basepath BASEPATH   : base path of the dataset
  --gpt_model GPT_MODEL
                        : model name for the generator LLM
  --dataset_source_dir DATASET_SOURCE_DIR
                        : directory path containing the Markdown files for the dataset
  --testset_test_size TESTSET_TEST_SIZE
                        : size of the test set
  --testset_comparative_query_ratio TESTSET_COMPARATIVE_QUERY_RATIO
                        : ratio of comparative query examples in the test set
  --testset_specific_query_ratio TESTSET_SPECIFIC_QUERY_RATIO
                        : ratio ofspecific query examples in the test set
  --testset_filename TESTSET_FILENAME
                        : path to save the generated test set
  --eval_result_filename EVAL_RESULT_FILENAME
                        : path to save the generated evaluation result
  --eval_metrics EVAL_METRICS
                        : list of evaluation metrics
  --eval_iterations EVAL_ITERATIONS
                        : number of evaluation iterations
```

### Actions

There's four different actions you can execute.

- createTestset

```bash
python trex_ragtools_aio.py --action createTestset --help
createTestset

        This function generates a test set using the LangChain library and saves it to a file.

        Arguments:
            --gpt_model (str): The model name for the generator LLM.
            --dataset_source_dir (str): The directory path containing the Markdown files for the dataset.
            --testset_test_size (int): The size of the test set.
            --testset_comparative_query_ratio(float): The ratio of comparative query examples in the test set.
            --testset_specific_query_ratio(float): The ratio ofspecific query examples in the test set.
            --testset_filename (str): The path to save the generated test set.
```

- generateContext

```bash
python trex_ragtools_aio.py --action generateContext --help
generateContext

        This function generates context for Ragas using a JSON file containing testset and saves it to a file.

        Arguments:
            --json_filename (str): The path to the input JSON file containing the testset.
            --testset_filename (str): The path to save the generated context file.
```

- evaluateTestset

```bash
python trex_ragtools_aio.py --action evaluateTestset --help
evaluateTestset

        Evaluates the performance of a GPT model on a given testset.
        evaluation metrics : LLMContextRecall, FactualCorrectness, Faithfulness, SemanticSimilarity
        about ragas metrics : https://docs.ragas.io/en/v0.2.2/concepts/metrics/available_metrics/

        Arguments:
            --json_filename (str): The path to the input JSON file containing the testset.
            --gpt_model (str): The name of the GPT model to be evaluated.
            --eval_result_filename (str): The path to save the generated evaluation result.
            --eval_metrics (list): The list of evaluation metrics
            --eval_iterations (int): Number of evaluation iterations
```

- parseTestset

```bash
python trex_ragtools_aio.py --action parseTestset --help
parseTestset

        Parses a JSON file containing a testset and saves it as a CSV file.

        Arguments:
            --json_filename (str): The path to the input JSON file.
            --csv_filename (str): The path to save the output CSV file.
            --eval_metrics (list): The list of evaluation metrics
```

### Arguments Examples

There's two ways to run the trex_ragtools_ai.py with arguments.

1. Using command line arguments

For example if you want to run createTest action with command line arguments, follow the instructions below.

```bash
python trex_ragtools_aio.py --action createTestset\
    --gpt_model gpt-4o-mini\
    --dataset_source_dir /path/to/dataset\
    --testset_comparative_query_ratio 0.5\
    --testset_specific_query_ratio 0.5\
    --testset_test_size 10\
    --testset_filename sample.json
```

2. Using json configuration

Write the `config.json` file like below.

```json
{
    "action": "createTestset",
    "json_filename": "./testset_with_context.json",
    "csv_filename": "",
    "basepath": "",
    "gpt_model": "gpt-4o-mini",
    "dataset_source_dir": "/path/to/dataset",
    "testset_test_size": 2,
    "testset_comparative_query_ratio": 0.5,
    "testset_specific_query_ratio": 0.5,
    "testset_filename": "./testset.json",
    "eval_result_filename": "./eval_result.json",
    "eval_metrics": ["LLMContextRecall", "FactualCorrectness", "Faithfulness", "SemanticSimilarity"],
    "eval_iterations": 3
}
```

Then run the main script with json configuration like this.

```bash
python trex_ragtools_aio.py --json_config ./config.json
```