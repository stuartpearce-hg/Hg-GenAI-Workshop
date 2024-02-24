from crewai import Crew
from textwrap import dedent

from agents.software_agents import SoftwareAgents
from tasks.software_tasks import SoftwareDevelopmentTasks


class SoftwareCrew:


  def run(self):
    agents = SoftwareAgents()
    tasks = SoftwareDevelopmentTasks()

    architect_agent = agents.architect()
    senior_engineer_agent = agents.senior_engineer()    
    quality_agent = agents.quality_assurance()

    planning_task = tasks.planning(architect_agent)
    implementation_task = tasks.implementation(senior_engineer_agent)
    review_task = tasks.review(architect_agent)

    crew = Crew(
      agents=[
        architect_agent,
        senior_engineer_agent,
        quality_agent
      ],
      tasks=[
        planning_task,
        implementation_task,
        review_task
      ],
      verbose=True
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
  print("## Welcome to GenAI Software Crew")
  print('-------------------------------')
  
  software_crew = SoftwareCrew()
  result = software_crew.run()
  print("\n\n########################")
  print("## Here is the Report")
  print("########################\n")
  print(result)
