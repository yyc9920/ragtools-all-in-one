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

load_dotenv()


class RagasTestsetCreator:
    def __init__(self, logger):
        self.logger = logger

    def load_markdown(self, data_path):
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
                # Document 객체의 metadata 속성에 파일명 추가
                doc.metadata["location"] = domain

            return documents

    def load_txt(self, data_path):
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
                # Document 객체의 metadata 속성에 파일명 추가
                doc.metadata["location"] = domain

            return documents

    def load_general(self, base_dir):
        data = []
        cnt = 0
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if ".txt" in file:
                    cnt += 1
                    data += self.load_txt(os.path.join(root, file))

        self.logger.info(f"the number of txt files is : {cnt}")
        return data

    def load_document(self, base_dir):
        data = []
        cnt = 0
        for root, _, files in os.walk(base_dir):
            for file in files:
                if ".md" in file:
                    cnt += 1
                    data += self.load_markdown(os.path.join(root, file))

        self.logger.info(f"the number of md files is : {cnt}")
        return data

    def X_get_markdown_files(self, source_dir):
        dir_ = source_dir
        loader = DirectoryLoader(
            dir_,
            glob="**/*.md",
            loader_cls=UnstructuredMarkdownLoader)
        documents = loader.load()
        return documents

    def get_markdown_files(self, source_dir):
        md_data = self.load_document(base_dir=source_dir)
        text_data = self.load_general(base_dir=source_dir)

        return md_data + text_data

    def save_test_set(self, test_set, file_path):
        if file_path is None:
            return False

        if not file_path.endswith(".json"):
            file_path += ".json"

        self.logger.info(f"Test set : {json.dumps(test_set.dict()['samples'][-1], indent=4)}")
        evaluation_dataset = test_set.to_evaluation_dataset()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_dataset.dict(), f, indent=4)
        self.logger.info(f"Save to json file : {file_path}")

    def main(
            self,
            source_dir,
            test_size,
            comparative_query_ratio,
            specific_query_ratio,
            model,
            testset_filename):
        generator_llm = ChatOpenAI(model=model)
        generator = TestsetGenerator.from_langchain(generator_llm)
        md_files = self.get_markdown_files(source_dir=source_dir)
        self.logger.info(md_files[-1])
        ragas_llm = LangchainLLMWrapper(ChatOpenAI(model=model))
        self.logger.info("Generating ragas testset")
        test_set = generator.generate_with_langchain_docs(
            md_files, testset_size=test_size, query_distribution=[
                (ComparativeAbstractQuerySynthesizer(
                    llm=ragas_llm), comparative_query_ratio),
                (SpecificQuerySynthesizer(
                        llm=ragas_llm), specific_query_ratio),],
            with_debugging_logs=True)
        self.logger.info("Generating ragas testset Complete!!")
        self.logger.info(test_set)
        self.save_test_set(test_set=test_set, file_path=testset_filename)

        return test_set, generator
