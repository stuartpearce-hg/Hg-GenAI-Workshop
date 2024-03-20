from langchain_community.vectorstores import FAISS
from langchain.schema.messages import SystemMessage
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter

from workshop.integration import get_embeddings, get_qa
from workshop.config import get_repo_path, get_db_path, get_similarity_threshold, get_output_path

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
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
            search_type="mmr",
            search_kwargs={"k": 20, "fetch_k": 50},
        )
        embeddings_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=get_similarity_threshold())
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=embeddings_filter, base_retriever=retriever
)
        [qa, memory] = get_qa(retriever=compression_retriever)
        console.log('Loading [cyan]Chat Bot -> [green]DONE')
    except Exception:
        console.log('Loading [cyan]Chat Bot -> [red]FAILED')


# ----- Prompt Loop

# qa(
#     """
#     This conversation is about a codebase, this codebase is written in PHP and includes frameworks x,y,z. Please constrain all answers to be about this codebase.
#     """
# )

file = Path(get_output_path(), "QnALog.txt")
with open(file, 'w') as csp:
    while True:
        question = Prompt.ask("Question")
        csp.write('Question:' + question + '\n')

        if question == "quit":
            break
        if question == "undo":
            memory.chat_memory.messages.pop()
            memory.chat_memory.messages.pop()
            continue

        with console.status('Querying') as q:
            result = qa.invoke(question)
            print(Panel(Markdown(result['answer']), title=result['question'], padding=1))
            csp.write('Answer:' + result['answer'] + '\n')
