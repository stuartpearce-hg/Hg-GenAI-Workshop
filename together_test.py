from langchain_together import Together
from workshop.integration_together import get_llm

llm = get_llm()

input_ = """You are a teacher with a deep knowledge of machine learning and AI. \
You provide succinct and accurate answers. Answer the following question: 

What is a large language model?"""
try:
    print(llm.invoke(input_))
except Exception as e:
    print(e.with_traceback())

