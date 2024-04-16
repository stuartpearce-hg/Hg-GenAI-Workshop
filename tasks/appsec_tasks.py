from crewai import Task
from textwrap import dedent
from workshop.integration_anthropic import get_llm, get_jira_toolkit, get_github_toolkit
from tools.rag_tool import GetCode
from crewai_tools import GithubSearchTool
from workshop.config import get_repo_path, get_github_repo, get_github_config

class AppSecTasks():
  def __init__(self) -> None:
        self.jira_toolkit = get_jira_toolkit()
        self.github_toolkit = get_github_toolkit()
        self.rag_tool = GetCode()
        #self.rag_tool = GithubSearchTool(get_github_config())

  def code_review(self, agent):
    return Task(description=dedent(f"""
        Review the code in the repository from the base branch for application security vulnerabilities. Describe each vulnerability found and provide a recommendation for how to fix it.
      """),
      agent=agent,
      tools=self.github_toolkit.get_tools()
    )
  
  def rag_code_review(self, agent):
    return Task(description=dedent(f"""
        Review the source code for application security vulnerabilities. Summarise any vulnerabilities found and provide a recommendation for how to fix them.
      """),
      agent=agent,
      tools=[self.rag_tool]
    )

  def get_ticket_to_fix(self, agent):
    return Task(description="Search project AC for issues of type Bug that are assigned to you.",
      expected_output='A summary of the ticket number and issue description for each ticket found.',
      agent=agent,
      tools=self.jira_toolkit.get_tools()
    )

  def raise_tickets(self, agent): 
    return Task(description=dedent(f"""
        Create new Jira Bug issues in project AC for each vulnerability.
      """),
      agent=agent,
      tools=self.jira_toolkit.get_tools()
    )

  def create_branch(self, agent):
        return Task(description=dedent(f"""
            Create a new branch to use for work on this ticket. 
          """),
          agent=agent,
          tools=self.github_toolkit.get_tools()
      )

  def fix_issues(self, agent):
      return Task(description=dedent(f"""
          Review the source code, update the code as required to resolve the issues described.
        """),
        expected_output='A new branch containing a commit for the code changes to fix issues',
        agent=agent,
        tools=self.github_toolkit.get_tools()
    )
   
  def create_PR(self, agent):
      return Task(description=dedent(f"""
          Raise a pull request for the changes developed. 
        """),
        agent=agent,
        tools=self.github_toolkit.get_tools()
    )

  def review(self, agent):
    return Task(description=dedent(f"""
        Review the open pull requests and add a comment to provide feedback to the developer.
      """),
      expected_output='Comments added to the PR informing the developer of feedback to consider.',
      agent=agent,
      tools=self.github_toolkit.get_tools()
    )

  
