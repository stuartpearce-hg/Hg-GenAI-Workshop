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
    appsec_engineer = agents.appsec_engineer()
    ticket_manager = agents.ticket_manager()    
    code_manager = agents.code_manager()

    #code_review_task = tasks.code_review(appsec_engineer)
    #rag_code_review_task = tasks.rag_code_review(appsec_engineer)
    assign_ticket_task = tasks.get_ticket_to_fix(senior_engineer_agent)
    #tickets_task = tasks.raise_tickets(senior_engineer_agent)
    #create_branch_task = tasks.create_branch(appsec_engineer)
    fix_issues_task = tasks.fix_issues(appsec_engineer)
    #create_pr_task = tasks.create_PR(appsec_engineer)
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

    # crew = Crew(
    #   agents=[
    #     appsec_engineer
    #   ],
    #   tasks=[
    #     rag_code_review_task,
    #   ],
    #   verbose=True
    # )

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
