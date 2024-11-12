import itertools

from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.txt import TextParser
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import Language
from langchain_community.document_loaders.parsers.language.language_parser import LANGUAGE_EXTENSIONS, LANGUAGE_SEGMENTERS, LanguageParser

from pathlib import Path

from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.prompt import Confirm
from rich.table import Table

from workshop.integration import get_embeddings
from workshop.loaders import TextBlobLoader, FileSystemModel, TextBlobListLoader
from workshop.config import get_repo_path, get_db_path
from workshop.splitters import PHPTextSplitter, CSharpTextSplitter
from workshop.parsers import PHPSegmenter
from langchain.document_loaders.helpers import detect_file_encodings

console = Console()

LANGUAGE_EXTENSIONS['php'] = Language.PHP
LANGUAGE_EXTENSIONS['module'] = Language.PHP
LANGUAGE_EXTENSIONS['inc'] = Language.PHP

LANGUAGE_SEGMENTERS[Language.PHP] = PHPSegmenter

models = [
    # bVenus
    FileSystemModel(
        get_repo_path(), 
        includes=['./**/*'], 
        suffixes=['.php', '.html', '.js', '.cs', '.csproj', '.sln', '.json', '.md', '.yml', '.yaml', '.sh', '.py', '.css', '.sql', '.vbp', '.frm', '.bas', '.cls', '.abap', '.asddls', '.asbdef'],
    ),
    # src
    # FileSystemModel(
    #     get_repo_path(),
    #     includes=['./src/**/*'],
    #     suffixes=['.cs', '.csproj', '.sln', '.xml'],
    # ),
]


def merge_models(models):
    return itertools.chain(*[m.yield_paths() for m in models])


progress_cols = [
    '{task.description}',
    SpinnerColumn(),
    BarColumn(),
    MofNCompleteColumn(),
    TimeElapsedColumn()
]

try:
    # Make sure the database path exists
    Path(get_db_path()).mkdir(parents=True, exist_ok=True)

    with Progress(*progress_cols) as p:
        task_export = p.add_task('Exporting Context Paths', total=None)

        with open(f"{get_db_path()}/context_paths", 'w') as f:
            for pa in p.track(merge_models(models), task_id=task_export):
                f.write(f'{str(pa)}\n')
        p.stop_task(task_export)

        task_load = p.add_task('Loading Documents', total=None)

        blob_loader = TextBlobListLoader(paths=p.track(merge_models(models), task_id=task_load))
        loader = GenericLoader(blob_loader, TextParser())
        
        documents = loader.load()

        p.stop_task(task_load)

        task_text = p.add_task('Splitting Texts')
        python_splitter = CSharpTextSplitter(
            chunk_size=6000, 
            chunk_overlap=200
        )
        texts = python_splitter.split_documents(p.track(documents, task_id=task_text))
except Exception:
    console.print_exception(show_locals=True)
    raise

results = Table(title="Code Input")
results.add_column("Item", style="cyan")
results.add_column("Count", justify="right")
results.add_row("Documents", f"{len(documents)}")
results.add_row("Texts", f"{len(texts)}")

print(results)

if not Confirm.ask('Compute model?'):
    exit()

with Progress(*progress_cols) as p:

    task_embed = p.add_task('Processing Embeddings', total=None)
    embeddings = get_embeddings()
    db = FAISS.from_documents(texts, embeddings)
    p.stop_task(task_embed)

    task_save = p.add_task('Saving Database', total=None)

    db.save_local(get_db_path())
    p.stop_task(task_save)
