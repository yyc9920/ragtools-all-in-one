import os
import json
import chardet

from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import CharacterTextSplitter
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.synthesizers.specific_query import SpecificQuerySynthesizer
from ragas.testset.synthesizers.abstract_query import ComparativeAbstractQuerySynthesizer
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


def load_markdown(data_path):
    with open(data_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    with open(data_path, 'rt', encoding=encoding) as file:
        data_string = file.read()
        documents = markdown_splitter.split_text(data_string)

        # 파일명을 metadata에 추가
        domain = data_path  # os.path.basename(data_path)
        for doc in documents:
            if not doc.metadata:
                doc.metadata = {}
            doc.metadata["domain"] = domain  # Document 객체의 metadata 속성에 파일명 추가

        return documents


def load_txt(data_path):
    with open(data_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    text_splitter = CharacterTextSplitter(
        separator="\n",
        length_function=len,
        is_separator_regex=False,
    )

    with open(data_path, 'r', encoding=encoding) as file:
        data_string = file.read().split("\n")
        domain = data_path  # os.path.basename(data_path)
        documents = text_splitter.create_documents(data_string)

        for doc in documents:
            if not doc.metadata:
                doc.metadata = {}
            doc.metadata["domain"] = domain  # Document 객체의 metadata 속성에 파일명 추가

        return documents


def load_general(base_dir):
    data = []
    cnt = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if ".txt" in file:
                cnt += 1
                data += load_txt(os.path.join(root, file))

    print(f"the number of txt files is : {cnt}")
    return data


def load_document(base_dir):
    data = []
    cnt = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            if ".md" in file:
                cnt += 1
                data += load_markdown(os.path.join(root, file))

    print(f"the number of md files is : {cnt}")
    return data


def X_get_markdown_files(source_dir):
    dir_ = source_dir
    loader = DirectoryLoader(dir_, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()
    return documents


def get_markdown_files(source_dir):
    md_data = load_document(base_dir=source_dir)
    text_data = load_general(base_dir=source_dir)

    return md_data + text_data


def save_test_set(test_set, file_path):
    print(__name__)
    if file_path is None:
        return False

    if not file_path.endswith(".json"):
        file_path += ".json"

    evaluation_dataset = test_set.to_evaluation_dataset()

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_dataset.dict(), f, indent=4)
    print(f"Save to json file : {file_path}")


def main(source_dir, test_size, comparative_query_ratio, specific_query_ratio, model, testset_filename):
    generator_llm = ChatOpenAI(model=model)
    generator = TestsetGenerator.from_langchain(generator_llm)
    md_files = get_markdown_files(source_dir=source_dir)
    ragas_llm = LangchainLLMWrapper(ChatOpenAI(model=model))
    test_set = generator.generate_with_langchain_docs(md_files,
                                                      testset_size=test_size,
                                                      query_distribution=[
                                                          (ComparativeAbstractQuerySynthesizer(llm=ragas_llm), comparative_query_ratio),
                                                          (SpecificQuerySynthesizer(llm=ragas_llm), specific_query_ratio),],
                                                      with_debugging_logs=True)
    save_test_set(test_set=test_set, file_path=testset_filename)


if __name__ == "__main__":
    source_dir = rf"/Users/yechanyun/YYC/work/project/AI_Application/rag/data/exynos-ai-studio-docs-main"
    # source_dir = rf"C:\\work\\project\\AI_Application\\rag\\data\\exynos-ai-studio-docs-main"
    test_size = 10
    simple_ratio = 0.5
    reasoning_ratio = 0.5
    model = "gpt-4o-mini"
    print("given from test_set_creator.py")

    # main 함수 실행
    main(source_dir=source_dir, test_size=test_size, comparative_query_ratio=simple_ratio, specific_query_ratio=reasoning_ratio,
         model=model, testset_filename="./sample.json")
