
import dotenv
import os

dotenv.load_dotenv()

database_path = os.getenv('DATABASE_PATH', './databases/current')

azure_endpoint = os.getenv('AZURE_ENDPOINT')
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_api_type = os.getenv('OPENAI_API_TYPE')
openai_api_version = os.getenv('OPENAI_API_VERSION')

openai_deployment = os.getenv('OPENAI_API_DEPLOYMENT_NAME')
openai_deployment_embeddings = os.getenv('OPENAI_API_EMBEDDINGS_NAME')

together_api_key = os.getenv('TOGETHER_API_KEY')
together_deployment_embeddings = os.getenv('TOGETHER_EMBEDDINGS_MODEL')
together_chat_model = os.getenv('TOGETHER_CHAT_MODEL')

anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
anthropic_chat_model = os.getenv('ANTHROPIC_CHAT_MODEL')

repository_path = os.getenv('REPOSITORY_DIRECTORY')
output_path = os.getenv('CODEGEN_OUTPUT_PATH')
temperature = os.getenv('QUERY_TEMPERATURE', 0.7)
similarity_threshold = os.getenv('SIMILARITY_THRESHOLD', 0.7)

jira_username = os.getenv('JIRA_EMAIL')
jira_instance_url = os.getenv('JIRA_SERVER')
jira_api_token = os.getenv('JIRA_API_KEY')

github_app_id = os.getenv('GITHUB_APP_ID')
github_app_private_key = os.getenv('GITHUB_APP_PRIVATE_KEY')
github_repository = os.getenv('GITHUB_REPOSITORY')
github_branch = os.getenv('GITHUB_BRANCH')
github_base_branch = os.getenv('GITHUB_BASE_BRANCH')


def get_openai_config():
    return {
        'azure_endpoint': azure_endpoint,
        'api_key': openai_api_key,
        'openai_api_type': openai_api_type,
        'api_version': openai_api_version,
    }

def get_azure_endpoint():
    return azure_endpoint

def get_api_key():
    return openai_api_key

def get_api_type():
    return openai_api_type

def get_together_api_key():
    return together_api_key

def get_together_embeddings():
    return together_deployment_embeddings

def get_together_chat_model():
    return together_chat_model

def get_anthropic_api_key():
    return anthropic_api_key

def get_anthropic_chat_model():
    return anthropic_chat_model

def get_api_version():
    return openai_api_version

def get_repo_path():
    return repository_path

def get_output_path():
    return output_path


def get_query_temperature():
    return temperature

def get_similarity_threshold():
    return similarity_threshold

def get_db_path():
    return database_path

def get_jira_config():
    return {
        'jira_username': jira_username,
        'jira_instance_url': jira_instance_url,
        'jira_api_token': jira_api_token
    }

def get_github_config():
    return {
        'github_app_id': github_app_id,
        'github_app_private_key': github_app_private_key,
        'github_repository': github_repository,
        'github_base_branch': github_base_branch
   }

def get_github_repo():
    return github_repository

