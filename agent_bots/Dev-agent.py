import os
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, AgentExecutor, create_structured_chat_agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper
from langchain_openai import OpenAI
from langchain_openai import AzureChatOpenAI
from langchain import hub

load_dotenv()
    
os.environ["JIRA_API_TOKEN"] = os.environ.get("JIRA_API_KEY")
os.environ["JIRA_USERNAME"] = os.environ.get("JIRA_EMAIL")
os.environ["JIRA_INSTANCE_URL"] = os.environ.get("JIRA_SERVER")
os.environ["GITHUB_APP_ID"] = os.environ.get("GITHUB_APP_ID")
os.environ["GITHUB_APP_PRIVATE_KEY"] = os.environ.get("GITHUB_APP_PRIVATE_KEY")
os.environ["GITHUB_REPOSITORY"] = os.environ.get("GITHUB_REPOSITORY")
os.environ["GITHUB_BRANCH"] = os.environ.get("GITHUB_BRANCH")
os.environ["GITHUB_BASE_BRANCH"] = os.environ.get("GITHUB_BASE_BRANCH")

llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION", "2023-07-01-preview"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt35"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<your-endpoint>.openai.azure.com/"),
    api_key=os.environ.get("AZURE_OPENAI_KEY"),
    temperature=0.3
    )
jira = JiraAPIWrapper()
jira_toolkit = JiraToolkit.from_jira_api_wrapper(jira)
github = GitHubAPIWrapper()
github_toolkit = GitHubToolkit.from_github_api_wrapper(github)
# Combine your tool with the json toolkit tools
combined_tools = jira_toolkit.get_tools() + github_toolkit.get_tools()

#agent = initialize_agent(
#    tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
#)
prompt = hub.pull("hwchase17/structured-chat-agent")
agent = create_structured_chat_agent(llm, combined_tools, prompt)

print("Available tools:")
for tool in combined_tools:
    print("\t" + tool.name)

agent_executor = AgentExecutor(agent=agent, tools=combined_tools, verbose=True, return_intermediate_steps=True)

agent_executor.invoke({"input": f"""
        Review the Github repository for security vulnerabilities.
        Plan the steps required to resolve any vulnerabilities found and create Jira issues in project AC for each step.
        Take each issue and create a branch from the base branch. Develop the fixes described by the issue. Once the fixes are developed, create a pull request to merge the branch into the base branch.
      """, "verbose":"True"})
#agent.run(f"""
#        Create a new issue in project AC to review the Github repository for security vulnerabilities.
#        Plan the steps required to resolve any vulnerabilities found.
#        Create a new issue in project AC for each steps identified in the plan. Set the parent item field to the parent issue.
#        Take each issue and create a branch from the base branch. Develop the functionality described by the issue. Once the functionality is developed, create a pull request to merge the branch into the base branch.
#      """)

