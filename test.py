from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from ragas.testset import TestsetGenerator
from ragas.testset.synthesizers.abstract_query import ComparativeAbstractQuerySynthesizer
# from ragas.testset.synthesizers.base import BaseSynthesizer
# from ragas.testset.synthesizers.base_query import QuerySynthesizer
from ragas.testset.synthesizers.specific_query import SpecificQuerySynthesizer
from ragas.llms import LangchainLLMWrapper

load_dotenv()

generator_llm = ChatOpenAI(model="gpt-4o-mini")
ragas_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
# critic_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))
# embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
generator = TestsetGenerator.from_langchain(generator_llm)
md_files = get_markdown_files(source_dir="/Users/yechanyun/YYC/work/project/AI_Application/rag/data/exynos-ai-studio-docs-main")
test_set = generator.generate_with_langchain_docs(md_files,
                                                  testset_size=10,
                                                  query_distribution=[
                                                    (ComparativeAbstractQuerySynthesizer(llm=ragas_llm), 0.5),
                                                    (SpecificQuerySynthesizer(llm=ragas_llm), 0.5),],
                                                  with_debugging_logs=True)


# In[13]:


test_set.dict()


# In[14]:


evaluation_dataset = test_set.to_evaluation_dataset()
evaluation_dataset
print(evaluation_dataset.dict())


# In[25]:


evaluation_dataset.to_jsonl("./evaluation_dataset.jsonl")


# In[26]:


test_set.to_jsonl("./testset.jsonl")


# In[1]:


from tsk_ragtools import text_gen as tg
from ragas import EvaluationDataset

evaluation_dataset = EvaluationDataset.from_jsonl('./evaluation_dataset.jsonl')
evaluation_dataset_dict = evaluation_dataset.dict()

for i, obj in enumerate(evaluation_dataset_dict["samples"]):
  print(
    f"\rGenerating RAGAS json...({i+1}/{len(evaluation_dataset_dict['samples'])})",
    end="",
    flush=True,
  )
  response = tg.answer_question(obj["user_input"])
  obj.update({"retrieved_contexts": response["list"], "response": response["response"]})

print(evaluation_dataset_dict)


# In[4]:


eval_dataset = EvaluationDataset.from_dict(mapping=evaluation_dataset_dict["samples"])


# In[5]:


from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity
from ragas import evaluate

from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))

metrics = [LLMContextRecall(), FactualCorrectness(), Faithfulness()]
results = evaluate(dataset=eval_dataset, metrics=metrics, llm=evaluator_llm,)


# In[8]:


results.to_pandas().to_dict()

