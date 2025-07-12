import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from ytm2lfm.database import SQLite

# Assuming the SQLite class code is already imported and available here


@pytest.fixture
def temp_db_path():
    with tempfile.TemporaryDirectory() as tmpdirname:
        db_path = os.path.join(tmpdirname, "test_scrobbles.db")
        yield db_path


def test_ensure_db_dir_creates_directory(temp_db_path):
    _ = SQLite(temp_db_path)
    assert Path(temp_db_path).parent.exists()


def test_init_db_creates_table(temp_db_path):
    db = SQLite(temp_db_path)
    with db.connect() as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scrobbles'")
        table = cursor.fetchone()
    assert table is not None


def test_insert_and_fetch_tracks(temp_db_path):
    db = SQLite(temp_db_path)
    tracks = [
        {"video_id": "vid1", "title": "title1", "artist": "artist1", "album": "album1", "played": "Today"},
        {"video_id": "vid2", "title": "title2", "artist": "artist2", "album": "album2", "played": "Last Week"},
    ]
    n_inserted_rows = db.insert_tracks(tracks)
    rows = db.fetch_latest_scrobbles()
    assert len(rows) == n_inserted_rows == 2
    assert rows[0]["video_id"] == "vid2"  # Latest inserted first


def test_delete_all_tracks(temp_db_path):
    db = SQLite(temp_db_path)
    tracks = [
        {"video_id": "vid1", "title": "title1", "artist": "artist1", "album": "album1", "played": 1},
    ]
    db.insert_tracks(tracks)
    db.delete_all_tracks()
    rows = db.fetch_latest_scrobbles()
    assert len(rows) == 0


def test_delete_except_latest_n(temp_db_path):
    db = SQLite(temp_db_path)
    tracks = [
        {"video_id": f"vid{i}", "title": f"title{i}", "artist": f"artist{i}", "album": f"album{i}", "played": "Today"}
        for i in range(1, 6)
    ]
    db.insert_tracks(tracks)
    db.delete_except_latest_n(2)
    rows = db.fetch_latest_scrobbles()
    assert len(rows) == 2
    assert rows[0]["video_id"] == "vid5"
    assert rows[1]["video_id"] == "vid4"


def test_delete_except_latest_n_invalid_value(temp_db_path):
    db = SQLite(temp_db_path)
    with pytest.raises(ValueError):
        db.delete_except_latest_n(0)
