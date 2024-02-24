from crewai import Task
from textwrap import dedent

class SoftwareDevelopmentTasks():
  def planning(self, agent):
    return Task(description=dedent(f"""
        Find ticket to work on. 
        Plan the steps required to implement and test the functionality described by the Epic
        and create new tickets of type Story which describe each step. Link the new Stories to the Epic.
      """),
      agent=agent
    )
    
  def implementation(self, agent): 
    return Task(description=dedent(f"""
        Obtain the latest source code from Github and create a branch to work on the Epic.
        Develop the functionality described by the Epic and the Stories as well as accompanying unit tests.
        Update the ticket status to In Progress.
        Commit the changes to the branch, including the related ticket number in the commit description and push the branch to Github.
        Create a pull request to merge the branch into the main branch.
      """),
      agent=agent
    )

  def review(self, agent):
    return Task(description=dedent(f"""
        Review the pull request and provide feedback to the developer.
      """),
      agent=agent
    )

  
