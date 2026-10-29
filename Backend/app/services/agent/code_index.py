import io
import tarfile

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...core.db import SessionLocal
from ...core.llm import embeddings
from ...models.code_chunk import CodeChunk
from ...models.user import User
from ..github_service import get_github_bytes, get_token

CODE_EXTENSIONS = (".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rb", ".php", ".cs", ".rs",
                   ".c", ".h", ".cpp", ".hpp", ".swift", ".scala", ".sql", ".vue", ".svelte", ".sh")
SKIP_FOLDERS = {"node_modules", "vendor", "dist", "build", "venv", ".venv", "__pycache__", "migrations"}
LINES_PER_CHUNK = 60
MAX_FILE_SIZE = 100_000
MAX_DOWNLOAD_SIZE = 50_000_000
MAX_CHUNKS = 1000
SEARCH_RESULTS = 5


def index_repo(db: Session, user: User, repo: str):
    token = get_token(user, repo)
    repo_bytes = get_github_bytes(token, f"/repos/{repo}/tarball", MAX_DOWNLOAD_SIZE)
    archive = tarfile.open(fileobj=io.BytesIO(repo_bytes), mode="r:gz")

    chunks = []
    for file in archive.getmembers():
        if not file.isfile() or file.size > MAX_FILE_SIZE:
            continue

        file_path = file.name.split("/", 1)[1]
        if not is_code_file(file_path):
            continue

        file_text = archive.extractfile(file).read().decode(errors="ignore")
        chunks.extend(split_into_chunks(repo, file_path, file_text))

    if len(chunks) == 0:
        raise HTTPException(status_code=400, detail="No code files found to index")
    if len(chunks) > MAX_CHUNKS:
        raise HTTPException(status_code=400, detail=f"This repo is too big to index (more than {MAX_CHUNKS} chunks)")

    add_embeddings(chunks)

    db.query(CodeChunk).filter(CodeChunk.repo == repo).delete()
    db.add_all(chunks)
    db.commit()
    return len(chunks)


def is_code_file(file_path: str):
    if not file_path.endswith(CODE_EXTENSIONS):
        return False

    folders = file_path.split("/")
    for folder in folders:
        if folder in SKIP_FOLDERS:
            return False
    return True


def split_into_chunks(repo: str, file_path: str, file_text: str):
    all_lines = file_text.splitlines()
    chunks = []

    for start in range(0, len(all_lines), LINES_PER_CHUNK):
        chunk_lines = all_lines[start:start + LINES_PER_CHUNK]
        chunk = CodeChunk(
            repo=repo,
            path=file_path,
            start_line=start + 1,
            end_line=start + len(chunk_lines),
            content="\n".join(chunk_lines),
        )
        chunks.append(chunk)

    return chunks


def add_embeddings(chunks: list[CodeChunk]):
    texts = []
    for chunk in chunks:
        texts.append(chunk.path + "\n" + chunk.content)

    try:
        vectors = embeddings.embed_documents(texts, task_type="RETRIEVAL_DOCUMENT")
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Embedding failed: {error}")

    for i in range(len(chunks)):
        chunks[i].embedding = vectors[i]


def count_chunks(db: Session, user: User, repo: str):
    get_token(user, repo)

    count = db.query(CodeChunk).filter(CodeChunk.repo == repo).count()
    return count


def search_chunks(repo: str, question: str):
    question_vector = embeddings.embed_query(question, task_type="RETRIEVAL_QUERY")

    db = SessionLocal()
    try:
        chunks = db.query(CodeChunk)
        chunks = chunks.filter(CodeChunk.repo == repo)
        chunks = chunks.order_by(CodeChunk.embedding.cosine_distance(question_vector))
        chunks = chunks.limit(SEARCH_RESULTS).all()
    finally:
        db.close()
    return chunks
