from pathlib import Path
from .db import init_db
from .embeddings import embed_text
def ingest(corpus_dir="data/corpus", dsn=None):
    files=list(Path(corpus_dir).glob("*"))
    if dsn: init_db(dsn)
    return {"files_seen":len(files),"dsn":dsn,"embedding_dimension":len(embed_text("demo")),"status":"ready for document parsing and pgvector load"}
if __name__ == "__main__": print(ingest())

