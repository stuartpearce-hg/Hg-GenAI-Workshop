import os
from dotenv import load_dotenv
from langchain.tools import tool
from jira import JIRA

load_dotenv()

class JiraTools():

    @tool("Find Jira tickets")
    def find_tickets(query):
        """Useful to find Jira tickets"""
        jira_server = os.getenv('JIRA_SERVER')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_key = os.getenv('JIRA_API_KEY')
        jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_key))
        jql_str='type = "Epic" AND status = "To Do" AND Project = "AI Crew"'
        tickets = jira.search_issues(jql_str)
        return tickets
  
    @tool("Retrieve Jira ticket information")
    def fetch_ticket(ticket_id):
        """Useful to retrieve information about a Jira ticket"""
        jira_server = os.getenv('JIRA_SERVER')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_key = os.getenv('JIRA_API_KEY')
        jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_key))
        ticket = jira.issue(ticket_id)
        return ticket
    
    @tool("Create a Jira ticket")
    def create_ticket(project, summary, description):
        """Useful to create a Jira ticket"""
        jira_server = os.getenv('JIRA_SERVER')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_key = os.getenv('JIRA_API_KEY')
        jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_key))
        ticket = jira.create_issue(project=project, summary=summary, description=description)
        return ticket
    
    @tool("Update a Jira ticket")
    def update_ticket(ticket_id, summary, description):
        """Useful to update a Jira ticket"""
        jira_server = os.getenv('JIRA_SERVER')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_key = os.getenv('JIRA_API_KEY')
        jira = JIRA(server=jira_server, basic_auth=(jira_email, jira_api_key))
        ticket = jira.issue(ticket_id)
        ticket.update(summary=summary, description=description)
        return ticket