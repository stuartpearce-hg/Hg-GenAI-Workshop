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
    
    def ticket_manager(self):
        return Agent(
            role='Ticket Manager',
            goal="""Ensure the status of work is accurately tracked within Jira tickets""",
            backstory="""You help the team collaborate by tracking the latest status of work as it progresses. Updating tickets to ensure everyone is aware of progress""",
            verbose=True,
            llm=self.def_llm,
            tools=self.jira_toolkit.get_tools()
        )
    
    def code_manager(self):
        return Agent(
            role='Code Manager',
            goal="""Ensure source code is managed and tracked within GitHub repository supporting the development process""",
            backstory="""You keep track of changes to the source code and ensure branches of work are controlled via pull requests for review""",
            verbose=True,
            llm=self.def_llm,
            tools=self.github_toolkit.get_tools()
        )
    
    def appsec_engineer(self):
        return Agent(
            role='Experienced software engineer',
            goal="""Implement the most maintainable and scalable software adhering to industry best practices and design patterns""",
            backstory="""The most seasoned senior software engineer with 
            deep expertise developing modern SaaS platforms.""",
            verbose=True,
            llm=self.def_llm
        )