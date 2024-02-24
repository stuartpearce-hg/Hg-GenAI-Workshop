from crewai import Task
from textwrap import dedent

class AppSecTasks():
  def code_review(self, agent):
    return Task(description=dedent(f"""
        Review the code in the repository from the base branch for application security vulnerabilities. Describe each vulnerability found and provide a recommendation for how to fix it.
      """),
      agent=agent
    )
    
  def raise_tickets(self, agent): 
    return Task(description=dedent(f"""
        Identify the mandatory fields required for tickets of type Bug then Create new Jira Bug issues in project AC for each vulnerability.
      """),
      agent=agent
    )

  def fix_issues(self, agent):
      return Task(description=dedent(f"""
          Create a branch from the base branch. Develop the fixes required to resolve the issue. Once the fixes are developed, create a pull request to merge the branch into the base branch.
        """),
        agent=agent
    ) 


  def review(self, agent):
    return Task(description=dedent(f"""
        Review the open pull requests and provide feedback to the developer.
      """),
      agent=agent
    )

  
