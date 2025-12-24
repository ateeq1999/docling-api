"""SQLite vector store using sqlite-vec."""

import sqlite3
import struct

import sqlite_vec


def serialize_float32(vector: list[float]) -> bytes:
    """Serialize a float32 vector to bytes for sqlite-vec."""
    return struct.pack(f"{len(vector)}f", *vector)


class SQLiteVectorStore:
    """Vector store using SQLite with sqlite-vec extension."""

    def __init__(self, db_path: str = "docling.db", dimension: int = 384):
        self.db_path = db_path
        self.dimension = dimension
        self.conn = sqlite3.connect(db_path)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        self._init_tables()

    def _init_tables(self):
        """Initialize vector tables."""
        self.conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks
            USING vec0(embedding float[{self.dimension}])
        """)
        self.conn.commit()

    def add(self, chunk_id: int, embedding: list[float]):
        """Add a single embedding."""
        self.conn.execute(
            "INSERT INTO vec_chunks(rowid, embedding) VALUES (?, ?)",
            (chunk_id, serialize_float32(embedding)),
        )
        self.conn.commit()

    def add_batch(self, chunk_ids: list[int], embeddings: list[list[float]]):
        """Add multiple embeddings in a batch."""
        data = [
            (chunk_id, serialize_float32(emb))
            for chunk_id, emb in zip(chunk_ids, embeddings)
        ]
        self.conn.executemany(
            "INSERT INTO vec_chunks(rowid, embedding) VALUES (?, ?)",
            data,
        )
        self.conn.commit()

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[tuple[int, float]]:
        """Search for similar vectors.
        
        Returns:
            List of (chunk_id, distance) tuples, sorted by distance ascending.
        """
        results = self.conn.execute(
            """
            SELECT rowid, distance
            FROM vec_chunks
            WHERE embedding MATCH ?
            ORDER BY distance
            LIMIT ?
            """,
            (serialize_float32(query_embedding), top_k),
        ).fetchall()
        return results

    def delete(self, chunk_id: int):
        """Delete a single embedding."""
        self.conn.execute(
            "DELETE FROM vec_chunks WHERE rowid = ?",
            (chunk_id,),
        )
        self.conn.commit()

    def delete_batch(self, chunk_ids: list[int]):
        """Delete multiple embeddings."""
        self.conn.executemany(
            "DELETE FROM vec_chunks WHERE rowid = ?",
            [(cid,) for cid in chunk_ids],
        )
        self.conn.commit()

    def count(self) -> int:
        """Count total embeddings."""
        result = self.conn.execute(
            "SELECT COUNT(*) FROM vec_chunks"
        ).fetchone()
        return result[0] if result else 0

    def close(self):
        """Close the database connection."""
        self.conn.close()


_default_store: SQLiteVectorStore | None = None


def get_vector_store(dimension: int = 384) -> SQLiteVectorStore:
    """Get the default vector store (singleton)."""
    global _default_store
    if _default_store is None:
        _default_store = SQLiteVectorStore(dimension=dimension)
    return _default_store
