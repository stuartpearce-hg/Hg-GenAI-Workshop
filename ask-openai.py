import dotenv
import os
from langchain.document_loaders import TextLoader

from langchain.text_splitter import Language
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.directory import DirectoryLoader
from langchain.document_loaders.parsers.language import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationalRetrievalChain

dotenv.load_dotenv()

openai_api_base = os.getenv('OPENAI_API_BASE')
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_api_type = os.getenv('OPENAI_API_TYPE')
openai_api_version = os.getenv('OPENAI_API_VERSION')
openai_deployment_name = os.getenv('OPENAI_API_DEPLOYMENT_NAME')
openai_deployment_embeddings = os.getenv('OPENAI_API_EMBEDDINGS_NAME')

repo_path = "./tests"
loader = GenericLoader.from_filesystem(
    repo_path,
    glob="**/*",
    suffixes=[".py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=50)
)

documents = loader.load()
len(documents)

python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.CSHARP,
                                                               chunk_size=4000,
                                                               chunk_overlap=200)
texts = python_splitter.split_documents(documents)
len(texts)

embeddings = OpenAIEmbeddings(disallowed_special=(),
                              deployment=openai_deployment_embeddings,
                              openai_api_base=openai_api_base,
                              openai_api_key=openai_api_key,
                              openai_api_type=openai_api_type,
                              openai_api_version=openai_api_version, chunk_size=16)

# output_dir = "./db_metadata_v5"

# generate text embeddings for our target codebase
db = FAISS.from_documents(texts, embeddings)

retriever = db.as_retriever(
    search_type="mmr",  # Also test "similarity"
    search_kwargs={"k": 8},
)

llm = AzureChatOpenAI(deployment_name=openai_deployment_name,
                      openai_api_base=openai_api_base,
                      openai_api_version=openai_api_version,
                      openai_api_key=openai_api_key,
                      openai_api_type=openai_api_type,
                      temperature=0.3,  # use lower temperature for writing code (more precision), higher is ok for reading.
                      verbose=True)


memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)

while True:
    question = input("Ask a question: ")
    if question == "quit":
        break
    print("Question: ", question)

    result = qa(question)
    print("Answer: ", result['answer'])
