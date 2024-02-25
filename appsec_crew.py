from crewai import Crew
from textwrap import dedent

from agents.appsec_agents import AppSecAgents
from tasks.appsec_tasks import AppSecTasks


class AppSecCrew:


  def run(self):
    agents = AppSecAgents()
    tasks = AppSecTasks()

    architect_agent = agents.architect()
    senior_engineer_agent = agents.senior_engineer()    
    quality_agent = agents.quality_assurance()

    code_review_task = tasks.code_review(architect_agent)
    assign_ticket_task = tasks.get_ticket_to_fix(senior_engineer_agent)
    tickets_task = tasks.raise_tickets(senior_engineer_agent)
    fix_issues_task = tasks.fix_issues(architect_agent)
    review_task = tasks.review(architect_agent)

    crew = Crew(
      agents=[
        architect_agent,
        senior_engineer_agent,
        quality_agent
      ],
      tasks=[
        assign_ticket_task,
        fix_issues_task,
        review_task
      ],
      verbose=True
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
  print("## Welcome to GenAI Software AppSec Crew")
  print('-------------------------------')
  
  appsec_crew = AppSecCrew()
  result = appsec_crew.run()
  print("\n\n########################")
  print("## Here is the Report")
  print("########################\n")
  print(result)
