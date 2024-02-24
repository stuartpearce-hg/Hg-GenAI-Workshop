from crewai import Agent
import os
from dotenv import load_dotenv
from tools.calculator_tools import CalculatorTools
from tools.jira_tools import JiraTools
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper

from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_openai import AzureChatOpenAI

class SoftwareAgents():

  def_llm = ''
  toolkit = JiraAPIWrapper
  

  def __init__(self) -> None:
    load_dotenv()
    self.def_llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_OPENAI_VERSION", "2023-07-01-preview"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt35"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://<your-endpoint>.openai.azure.com/"),
    api_key=os.environ.get("AZURE_OPENAI_KEY")
    )
    os.environ["JIRA_API_TOKEN"] = os.environ.get("JIRA_API_KEY")
    os.environ["JIRA_USERNAME"] = os.environ.get("JIRA_EMAIL")
    os.environ["JIRA_INSTANCE_URL"] = os.environ.get("JIRA_SERVER")
    
    jira = JiraAPIWrapper()
    self.toolkit = JiraToolkit.from_jira_api_wrapper(jira)

  
  def senior_engineer(self):
    return Agent(
      role='Experienced software engineer',
      goal="""Implement the most maintainable and scalable software adhering to industry best practices and design patterns""",
      backstory="""The most seasoned senior software engineer with 
      deep expertise developing modern SaaS platforms.""",
      verbose=True,
      llm=self.def_llm,
      tools=[
        self.toolkit.get_tools(), JiraTools.create_ticket, JiraTools.update_ticket, JiraTools.find_tickets, JiraTools.fetch_ticket
      ]
    )

  def quality_assurance(self):
    return Agent(
      role='Test Engineer',
      goal="""Design robust test plans and test cases to ensure the highest quality of the software""",
      backstory="""You're skilled in designing test plans and test cases to ensure the highest quality of the software.""",
      verbose=True,
      llm=self.def_llm,
      tools=[
        self.toolkit.get_tools(), JiraTools.create_ticket, JiraTools.update_ticket, JiraTools.find_tickets, JiraTools.fetch_ticket
      ]
  )

  def architect(self):
    return Agent(
      role='SaaS Architect',
      goal="""Ensure the software is designed to be scalable, maintainable, secure and cost effective to operate in a public cloud environment""",
      backstory="""You're the most experienced architect with deep expertise designing modern SaaS platforms.""",
      verbose=True,
      llm=self.def_llm,
      tools=[
        self.toolkit.get_tools()
      ]
    )