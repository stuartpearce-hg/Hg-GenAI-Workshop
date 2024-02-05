
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

repository_path = os.getenv('REPOSITORY_DIRECTORY')
temperature = os.getenv('QUERY_TEMPERATURE', 0.7)


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

def get_api_version():
    return openai_api_version

def get_repo_path():
    return repository_path


def get_query_temperature():
    return temperature


def get_db_path():
    return database_path
