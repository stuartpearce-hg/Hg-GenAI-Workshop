from crewai import Agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit

from langchain_openai import AzureChatOpenAI
from workshop.integration import get_llm, get_jira_toolkit, get_github_toolkit

class AppSecAgents():

    def_llm = ''
    jira_toolkit = JiraToolkit
    github_toolkit = GitHubToolkit

    def __init__(self) -> None:
        self.def_llm = get_llm()
        self.jira_toolkit = get_jira_toolkit()
        self.github_toolkit = get_github_toolkit()


  
    def senior_engineer(self):
        combined_tools = self.jira_toolkit.get_tools()
        combined_tools.extend(self.github_toolkit.get_tools() )
        return Agent(
            role='Experienced software engineer',
            goal="""Implement the most maintainable and scalable software adhering to industry best practices and design patterns""",
            backstory="""The most seasoned senior software engineer with 
            deep expertise developing modern SaaS platforms.""",
            verbose=True,
            llm=self.def_llm,
            tools=combined_tools
        )

    def quality_assurance(self):
        return Agent(
            role='Test Engineer',
            goal="""Design robust test plans and test cases to ensure the highest quality of the software""",
            backstory="""You're skilled in designing test plans and test cases to ensure the highest quality of the software.""",
            verbose=True,
            llm=self.def_llm,
            tools=self.jira_toolkit.get_tools()
        )

    def architect(self):
        combined_tools = self.jira_toolkit.get_tools()
        combined_tools.extend(self.github_toolkit.get_tools() )
        return Agent(
            role='SaaS Architect',
            goal="""Ensure the software is designed to be scalable, maintainable, secure and cost effective to operate in a public cloud environment""",
            backstory="""You're the most experienced architect with deep expertise designing modern SaaS platforms.""",
            verbose=True,
            llm=self.def_llm,
            tools=combined_tools
        )