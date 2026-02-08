import sqlite3
import json
from loguru import logger
from typing import Dict, Any, List
import threading
from datetime import datetime

class PacketStore:
    def __init__(self, db_path: str = "sentra_raw.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Create the packets table if it doesn't exist."""
        try:
            with self._get_conn() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS packets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        src_ip TEXT,
                        dst_ip TEXT,
                        size INTEGER,
                        protocol INTEGER,
                        src_port INTEGER,
                        dst_port INTEGER,
                        flags TEXT,
                        proto_name TEXT
                    )
                """)
                # Index for faster time-window queries
                conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON packets(timestamp)")
        except Exception as e:
            logger.error(f"Failed to init DB: {e}")

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def save_packet(self, data: Dict[str, Any]):
        """
        Save a single packet metadata to DB.
        """
        try:
            with self._lock:
                with self._get_conn() as conn:
                    conn.execute("""
                        INSERT INTO packets (timestamp, src_ip, dst_ip, size, protocol, src_port, dst_port, flags, proto_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data.get("timestamp"),
                        data.get("src_ip"),
                        data.get("dst_ip"),
                        data.get("size"),
                        data.get("protocol"),
                        data.get("src_port"),
                        data.get("dst_port"),
                        data.get("flags"),
                        data.get("proto_name")
                    ))
        except Exception as e:
            logger.error(f"Failed to save packet: {e}")

    def fetch_window(self, start_ts: float, end_ts: float) -> List[Dict[str, Any]]:
        """
        Fetch all packets within a time window.
        """
        try:
            with self._get_conn() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM packets WHERE timestamp >= ? AND timestamp < ?
                """, (start_ts, end_ts))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch window: {e}")
            return []

if __name__ == "__main__":
    store = PacketStore("test.db")
    sample = {
        "timestamp": datetime.now().timestamp(),
        "src_ip": "192.168.1.5",
        "dst_ip": "8.8.8.8",
        "size": 64,
        "protocol": 6,
        "src_port": 12345,
        "dst_port": 80,
        "flags": "S",
        "proto_name": "TCP"
    }
    store.save_packet(sample)
    print(f"Saved. Fetching...")
    print(store.fetch_window(0, 9999999999))
