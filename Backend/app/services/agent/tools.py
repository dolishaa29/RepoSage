from dataclasses import dataclass, field

from fastapi import HTTPException
from langchain.tools import ToolRuntime, tool

from ..github_service import call_github, get_raw_file, search_github_code
from .code_index import search_chunks

MAX_LINES = 300
MAX_FILES = 6


@dataclass
class Context:
    token: str
    repo: str
    ref: str
    originals: dict = field(default_factory=dict)
    changes: dict = field(default_factory=dict)


def get_text(context: Context, path: str):
    if not is_safe_path(path):
        raise HTTPException(status_code=400, detail="This path is not allowed")
    if path in context.changes:
        return context.changes[path]
    if path not in context.originals:
        context.originals[path] = get_raw_file(context.token, context.repo, path, context.ref)
    return context.originals[path]


@tool
def read_file(path: str, start_line: int, end_line: int, runtime: ToolRuntime[Context]) -> str:
    """Read lines start_line to end_line of a file in the repo (with line numbers). Read at most 300 lines at a time."""
    try:
        text = get_text(runtime.context, path)
    except HTTPException as e:
        return f"Error: {e.detail}"
    if text is None:
        return f"Error: {path} does not exist"
    lines = text.splitlines()
    start = max(start_line, 1)
    end = min(end_line, start + MAX_LINES - 1, len(lines))
    numbered = [f"{n}: {lines[n - 1]}" for n in range(start, end + 1)]
    return f"{path} has {len(lines)} lines. Showing {start}-{end}:\n" + "\n".join(numbered)


@tool
def list_files(folder: str, runtime: ToolRuntime[Context]) -> str:
    """List the files inside a folder of the repo. Use "" for the whole repo."""
    context = runtime.context
    try:
        tree = call_github(context.token, f"/repos/{context.repo}/git/trees/{context.ref}?recursive=1")["tree"]
    except HTTPException as e:
        return f"Error: {e.detail}"
    prefix = folder.strip("/") + "/" if folder.strip("/") else ""
    paths = [item["path"] for item in tree if item["type"] == "blob" and item["path"].startswith(prefix)]
    if len(paths) > 200:
        return "\n".join(paths[:200]) + f"\n... and {len(paths) - 200} more, list a smaller folder"
    return "\n".join(paths) or "No files found"


@tool
def search_code(text: str, runtime: ToolRuntime[Context]) -> str:
    """Find where an exact word or name (function, class, variable) appears in the repo. Searches the default branch."""
    try:
        items = search_github_code(runtime.context.token, runtime.context.repo, text)
    except HTTPException as e:
        return f"Error: {e.detail}"
    results = []
    for item in items:
        fragments = " ... ".join(m["fragment"] for m in item.get("text_matches", []))
        results.append(f"{item['path']}: {fragments}")
    return "\n\n".join(results) or "Nothing found"


@tool
def semantic_search(question: str, runtime: ToolRuntime[Context]) -> str:
    """Find code by meaning, for example "where are passwords hashed". Works only if the repo was indexed. Line numbers can be old, check with read_file."""
    try:
        chunks = search_chunks(runtime.context.repo, question)
    except Exception as e:
        return f"Error: {e}"
    if len(chunks) == 0:
        return "This repo is not indexed yet, use search_code instead"
    return "\n\n".join(f"{c.path} lines {c.start_line}-{c.end_line}:\n{c.content}" for c in chunks)


@tool
def edit_file(path: str, old_text: str, new_text: str, runtime: ToolRuntime[Context]) -> str:
    """Replace old_text with new_text in a file. old_text must be copied exactly from the file (without line numbers) and must appear only once."""
    context = runtime.context
    error = check_path(context, path)
    if error:
        return error
    try:
        text = get_text(context, path)
    except HTTPException as e:
        return f"Error: {e.detail}"
    if text is None:
        return f"Error: {path} does not exist, use create_file"
    if "\r\n" in text:
        old_text = old_text.replace("\r\n", "\n").replace("\n", "\r\n")
        new_text = new_text.replace("\r\n", "\n").replace("\n", "\r\n")
    count = text.count(old_text)
    if old_text == "" or count == 0:
        return "Error: old_text was not found. Read the file again and copy the lines exactly"
    if count > 1:
        return f"Error: old_text was found {count} times. Add more lines around it so it is unique"
    context.changes[path] = text.replace(old_text, new_text, 1)
    return f"Edited {path}"


@tool
def create_file(path: str, content: str, runtime: ToolRuntime[Context]) -> str:
    """Create a new file, for example a unit test. It cannot overwrite a file that already exists."""
    context = runtime.context
    error = check_path(context, path)
    if error:
        return error
    try:
        text = get_text(context, path)
    except HTTPException as e:
        return f"Error: {e.detail}"
    if text is not None:
        return f"Error: {path} already exists, use edit_file"
    context.originals[path] = ""
    context.changes[path] = content
    return f"Created {path}"


def is_safe_path(path: str):
    for part in path.split("/"):
        if part in ("", ".", ".."):
            return False
    return True


def check_path(context: Context, path: str):
    if path.startswith(".github/") or not is_safe_path(path):
        return "Error: you are not allowed to change this path"
    if path not in context.changes and len(context.changes) >= MAX_FILES:
        return f"Error: you can change at most {MAX_FILES} files"
    return None


READ_TOOLS = [read_file, list_files, search_code, semantic_search]
EDIT_TOOLS = READ_TOOLS + [edit_file, create_file]
