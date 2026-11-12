from dataclasses import dataclass
from .embeddings import embed_text

@dataclass
class Chunk:
    id: str; doc_id: str; section: str; page: int; text: str; score: float = 0.0

DEMO_CHUNKS = [
    Chunk("bis-market-risk-001", "bis-market-risk", "Minimum capital requirements for market risk", 1, "The market risk framework sets minimum capital requirements for market risk in the trading book." , .88),
    Chunk("sr11-7-001", "sr11-7", "Model risk management", 2, "Model risk is the potential for adverse consequences from decisions based on incorrect or misused model outputs. Banks should establish effective challenge and validation.", .84),
    Chunk("rbi-market-risk-001", "rbi-market-risk", "Market risk measurement", 3, "Banks should measure market risk using appropriate systems, controls, limits and periodic stress testing.", .82),
]

def search(query: str, k: int = 3, dsn: str | None = None) -> list[Chunk]:
    # Demo corpus fallback keeps the CLI useful before Postgres ingestion.
    q=set(query.lower().split())
    ranked=sorted(DEMO_CHUNKS, key=lambda c: (len(q & set(c.text.lower().split()))), reverse=True)
    return ranked[:k]

def search_pgvector(query: str, dsn: str, k: int = 3) -> list[Chunk]:
    """Search persisted chunks using pgvector cosine distance."""
    from psycopg import connect
    vector = embed_text(query)
    with connect(dsn) as conn:
        rows = conn.execute("SELECT id, doc_id, section, page, text_content, 1 - (embedding <=> %s) AS score FROM chunks WHERE embedding IS NOT NULL ORDER BY embedding <=> %s LIMIT %s", (vector, vector, k)).fetchall()
    return [Chunk(id=row[0], doc_id=row[1], section=row[2], page=row[3], text=row[4], score=float(row[5])) for row in rows]

