import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from ytm2lfm.logger import get_logger

logger = get_logger(__name__)


class SQLite:
    SCHEMA = """
        CREATE TABLE IF NOT EXISTS scrobbles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            played INTEGER NOT NULL
        )
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

        # ensure the directory for the database exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # initialize the database schema if it doesn't exist
        with self.connect() as conn:
            conn.execute(self.SCHEMA)

        logger.info(f"Database initialized at {self.db_path}")

    def connect(self, **kwargs):
        """Custom connect function that always sets row_factory to sqlite3.Row"""
        conn = sqlite3.connect(self.db_path, **kwargs)
        conn.row_factory = sqlite3.Row
        return conn

    def delete_all_tracks(self) -> int:
        """
        Delete all rows from the scrobbles table.

        Returns:
            Number of deleted rows
        """
        with self.connect() as conn:
            cursor = conn.execute("DELETE FROM scrobbles")
            deleted_count = cursor.rowcount

        logger.info(f"Deleted {deleted_count} tracks from scrobbles table")
        return deleted_count

    def insert_tracks(self, tracks: List[Dict[str, Any]]) -> int:
        """
        Bulk insert multiple scrobbles into the database.

        Args:
            tracks: List of track dictionaries

        Returns:
            Number of inserted rows
        """
        if not tracks:
            return 0

        with self.connect() as conn:
            cursor = conn.executemany(
                """
                INSERT INTO scrobbles (video_id, title, artist, album, played)
                VALUES (:video_id, :title, :artist, :album, :played)
                """,
                tracks,
            )
            count = cursor.rowcount

        return count

    def delete_except_latest_n(self, n: int) -> int:
        """
        Deletes all rows except the latest `n` records based on auto-incrementing ID.

        Args:
            n: Number of latest records to retain

        Returns:
            Number of deleted rows
        """
        if n < 1:
            raise ValueError("n must be a positive integer")

        with self.connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM scrobbles
                WHERE id <= (
                    SELECT id 
                    FROM scrobbles 
                    ORDER BY id DESC 
                    LIMIT 1 OFFSET ?
                )
                """,
                (n,),
            )
            deleted_count = cursor.rowcount

        return deleted_count

    def fetch_latest_scrobbles(self) -> List[Dict[str, Any]]:
        """
        Fetch all scrobbles from the database, ordered by ID descending.

        Returns:
            List of scrobble dictionaries
        """
        with self.connect() as conn:
            cursor = conn.execute("""
                SELECT video_id, title, artist, album, played
                FROM scrobbles
                ORDER BY id DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
