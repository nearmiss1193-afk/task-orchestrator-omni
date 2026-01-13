"""
Lightweight SQLite graph store for error relationships and knowledge graph.
"""
import sqlite3
import os
from datetime import datetime

class GraphStore:
    """Simple SQLite‑backed graph store.
    Nodes and edges are stored in two tables.
    """
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "graph_store.db")
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._ensure_schema()

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                data TEXT,
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src INTEGER NOT NULL,
                dst INTEGER NOT NULL,
                label TEXT,
                data TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(src) REFERENCES nodes(id),
                FOREIGN KEY(dst) REFERENCES nodes(id)
            )
        """)
        self.conn.commit()

    def add_node(self, label: str, data: str = None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO nodes (label, data, created_at) VALUES (?, ?, ?)",
            (label, data, datetime.utcnow().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def add_edge(self, src_id: int, dst_id: int, label: str = None, data: str = None) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO edges (src, dst, label, data, created_at) VALUES (?, ?, ?, ?, ?)",
            (src_id, dst_id, label, data, datetime.utcnow().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_node(self, node_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
        return cur.fetchone()

    def get_neighbors(self, node_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT dst FROM edges WHERE src = ?", (node_id,))
        return [row[0] for row in cur.fetchall()]

# Singleton for easy import
graph_store = GraphStore()
