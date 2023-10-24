from langchain.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory

from .config import openai_deployment, openai_deployment_embeddings, get_openai_config, get_query_temperature

def get_embeddings(disallowed_special=(), chunk_size=16):
    cfg = get_openai_config()
    
    return OpenAIEmbeddings(
        disallowed_special=disallowed_special, 
        chunk_size=chunk_size, 
        deployment=openai_deployment_embeddings,
        **cfg
    )

def get_qa(retriever, verbose=True):
    cfg = get_openai_config()

    llm = AzureChatOpenAI(
        deployment_name=openai_deployment,
        temperature=get_query_temperature(),
        verbose=verbose,
        **cfg
    )

    memory = ConversationSummaryMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=True
    )
    
    return [ConversationalRetrievalChain.from_llm(
        llm, 
        retriever=retriever, 
        memory=memory
    ), memory]