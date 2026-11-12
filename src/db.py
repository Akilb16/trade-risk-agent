from psycopg import connect
from pgvector.psycopg import register_vector

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS chunks (id text PRIMARY KEY, doc_id text NOT NULL, section text, page integer, text_content text NOT NULL, embedding vector(64), metadata jsonb DEFAULT '{}'::jsonb);
CREATE TABLE IF NOT EXISTS escalations (id bigserial PRIMARY KEY, question text NOT NULL, draft text, retrieved_ids jsonb, reason text NOT NULL, created_at timestamptz DEFAULT now(), status text DEFAULT 'open');
CREATE TABLE IF NOT EXISTS traces (id bigserial PRIMARY KEY, request_id uuid, model text, latency_ms double precision, tools jsonb, escalated boolean, created_at timestamptz DEFAULT now());
"""
def init_db(dsn: str):
    with connect(dsn) as conn: register_vector(conn); conn.execute(SCHEMA_SQL); conn.commit()
def save_escalation(dsn: str, question: str, draft: str, retrieved_ids: list[str], reason: str):
    with connect(dsn) as conn: conn.execute("INSERT INTO escalations(question,draft,retrieved_ids,reason) VALUES (%s,%s,%s,%s)", (question, draft, retrieved_ids, reason)); conn.commit()

