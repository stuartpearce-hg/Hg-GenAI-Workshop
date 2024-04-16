from langchain_community.vectorstores import FAISS
from langchain.schema.messages import SystemMessage

from workshop.integration import get_embeddings, get_qa
from workshop.config import get_repo_path, get_db_path, get_output_path

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from tqdm import tqdm
from pathlib import Path

console = Console()

db = None
qa = None

# --- Load Model & Chatbot

# system_message = SystemMessage(
#     content="""
#     This conversation is about a codebase, this codebase is written in PHP and includes frameworks x,y,z. Please constrain all answers to be about this codebase.
#     """
# )

with console.status('Starting...') as status:
    try:
        status.update('Loading [cyan]Context Database...')
        embeddings = get_embeddings()
        db = FAISS.load_local(get_db_path(), embeddings=embeddings)
        console.log('Loading [cyan]Context Database -> [green]DONE')
    except Exception:
        console.log('Loading [cyan]Context Database -> [red]FAILED')
        console.print_exception(show_locals=True)
        exit()
        
    try:
        status.update('Loading [cyan]Chat Bot...')
        retriever = db.as_retriever(
            search_type="mmr", # Also test "similarity"
            search_kwargs={"k": 20, "fetch_k": 50},
        )
        [qa, memory] = get_qa(retriever=retriever)
        console.log('Loading [cyan]Chat Bot -> [green]DONE')
    except Exception:
        console.log('Loading [cyan]Chat Bot -> [red]FAILED')


# ----- Prompt Loop

# qa(
#     """
#     This conversation is about a codebase, this codebase is written in PHP and includes frameworks x,y,z. Please constrain all answers to be about this codebase.
#     """
# )

# -- Generate BaseEntity class
result = qa.invoke("Create an abstract class named BaseEntity for other EntityFramework classes to inherit. Add a required property TenantID of type Guid. Respond with the full code for the updated file")
file = Path(get_output_path(), "BaseEntity.cs")
with open(file, 'w') as csp:
    csp.writelines(result['answer'])

with open ("EntityFiles.txt", 'r') as wsp:
    file_list = wsp.readlines() 

    file_list = [x.split("\n")[0] for x in file_list]

    errors = {}
    sql_server_sp = {}
    model_response = {}

    for file_name in tqdm(file_list, "Converting files..."):
        try:
            model_response[file_name] = qa.invoke("Modify the " + file_name + " file to also inherit BaseEntity, do not modify the current code in any other way. Respond with the full content for the updated file")
            file = Path(get_output_path(), file_name)
            with open(file, 'w') as csp:
                csp.writelines(model_response[file_name]['answer'])
            print("Processed " + file_name + " successfully")
            memory.chat_memory.clear()
        except Exception as e:
            errors[file_name] = e
            print("Error Processing " + file_name + ". Error: " + str(e))
