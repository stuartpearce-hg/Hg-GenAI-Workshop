from langchain_community.chat_models import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import AzureOpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory

from .config import openai_deployment, openai_deployment_embeddings, get_openai_config, get_query_temperature, get_azure_endpoint, get_api_key, get_api_type, get_api_version

def get_embeddings(disallowed_special=(), chunk_size=16):
    cfg = get_openai_config()
    
    return AzureOpenAIEmbeddings(
        azure_endpoint=get_azure_endpoint(),
        disallowed_special=disallowed_special, 
        chunk_size=chunk_size, 
        azure_deployment=openai_deployment_embeddings,
        api_key=get_api_key(),
        openai_api_type=get_api_type(),
        api_version=get_api_version()
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