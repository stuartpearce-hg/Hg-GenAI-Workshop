# Imports 
import requests

# Prerequisites 
    # OpenAI account
    # OpenAI key 

API_KEY = ""

chat_api_url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Model
model_name = "gpt-4"
temperature = 0.3
max_tokens = 2000

# System Setup
system_message = {
    "role": "system",
    "content": "You help convert SQL Server Stored Procedures to PostgreSQL Stored Procedures. \
        You are a confindant Assistant. Make sure that the bits in SQL server are translated to boolean of Postgres \
        Make the CameCase column names in doublequotes.\
        Only repond with conveted SQL.\
        Make sure the datatypes match the schema of tables provided. "
}

# funcs to chat

def send_request(conv):
    data = {
        "model": model_name,
        "temperature" : temperature,
        "max_tokens" : 2000,
        "messages" : conv,
        # "stream":True
    }
    return requests.post(url=chat_api_url, json=data, headers=headers, stream=True)

def send_request_to_azure(conv):
    api_base=""
    api_key=""
    deployment_id=""

    api_endpoint = f"{api_base}/openai/deployments/{deployment_id}/chat/completions?api-version=2023-08-01-preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        # "model": model_name,
        "temperature" : temperature,
        "max_tokens" : 2000,
        "messages" : conv,
        # "stream":True
    }

    return requests.post(url=api_endpoint, json=data, headers=headers)

def convert_to_postgreSQL(SQLserver_ps):

    conversation = [system_message]

    current_message = {"role":"user", "content":str(SQLserver_ps)}
    conversation = conversation +[current_message]
    return send_request_to_azure(conversation)
    
