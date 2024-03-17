from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import AzureOpenAIEmbeddings
from langchain.memory import ConversationSummaryMemory
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_community.document_transformers import LongContextReorder
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers import ContextualCompressionRetriever

from .config import openai_deployment, openai_deployment_embeddings, get_openai_config, get_query_temperature, get_azure_endpoint, get_api_key, get_api_type, get_api_version, get_jira_config, get_github_config

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
    
    reordering = LongContextReorder()

    pipeline_compressor = DocumentCompressorPipeline(
        transformers=[
            reordering
        ]
    )

    compression_retriever = ContextualCompressionRetriever(base_compressor=pipeline_compressor, base_retriever=retriever)

    #qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=compression_retriever, memory=memory, return_source_documents=True)

    return [ConversationalRetrievalChain.from_llm(
        llm, 
        retriever=compression_retriever, 
        memory=memory
    ), memory]

def get_llm():
    cfg = get_openai_config()

    return AzureChatOpenAI(
        deployment_name=openai_deployment,
        temperature=get_query_temperature(),
        verbose=True,
        **cfg
   )

def get_jira_toolkit():
    cfg = get_jira_config()
    jira = JiraAPIWrapper(**cfg)
    return JiraToolkit.from_jira_api_wrapper(jira)

def get_github_toolkit():
    cfg = get_github_config()
    github = GitHubAPIWrapper(**cfg)
    return GitHubToolkit.from_github_api_wrapper(github)