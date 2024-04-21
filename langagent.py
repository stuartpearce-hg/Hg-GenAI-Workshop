from workshop.integration import get_embeddings, get_llm
from langchain_community.vectorstores import FAISS
from workshop.config import get_repo_path, get_db_path, get_output_path
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

embeddings = get_embeddings()
db = FAISS.load_local(get_db_path(), embeddings=embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(
            search_type="mmr", # Also test "similarity"
            search_kwargs={"k": 20, "fetch_k": 30},
        )
retriever_tool = create_retriever_tool(
    retriever,
    "codebase_search",
    "Search for information about application source code. For any questions about the application or its code, you must use this tool!",
)
tools = [retriever_tool]

llm = get_llm()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a software coding assistant"),
        MessagesPlaceholder("Review the codebase for security vulnerabilities and provide a code changes to fix the vulnerabilities.", optional=True),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)
agent = create_openai_tools_agent(llm, tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke({"input": "Review the codebase for security vulnerabilities then provide code changes to fix all vulnerabilities found."})