from crewai import Task
from textwrap import dedent

class AppSecTasks():
  def code_review(self, agent):
    return Task(description=dedent(f"""
        Review the code in the repository from the base branch for application security vulnerabilities. Describe each vulnerability found and provide a recommendation for how to fix it.
      """),
      agent=agent
    )

  def get_ticket_to_fix(self, agent):
    return Task(description=dedent(f"""
        Search project AC for issues of type Bug that are assigned to you.
      """),
      agent=agent
    )

  def raise_tickets(self, agent): 
    return Task(description=dedent(f"""
        Create new Jira Bug issues in project AC for each vulnerability.
      """),
      agent=agent
    )

  def fix_issues(self, agent):
      return Task(description=dedent(f"""
          Develop the fixes required to resolve the issue on a new branch for this ticket. 
          Once the code has been comitted and pushed to the repository, create a pull request to merge the branch into the base branch.
        """),
        agent=agent
    ) 


  def review(self, agent):
    return Task(description=dedent(f"""
        Review the open pull requests and provide feedback to the developer.
      """),
      agent=agent
    )

  
