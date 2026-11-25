import os
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def app_module(tmp_path_factory):
    """Import app.py against a small temporary shows.db.

    app.py opens "sqlite:///shows.db" relative to the working directory at
    import time, and the real database is not in the repo, so build a tiny one.
    """
    workdir = tmp_path_factory.mktemp("db")
    conn = sqlite3.connect(workdir / "shows.db")
    conn.execute(
        "CREATE TABLE shows (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
        "year NUMERIC, episodes INTEGER)"
    )
    conn.executemany(
        "INSERT INTO shows (title, year, episodes) VALUES (?, ?, ?)",
        [
            ("The Office", 2005, 201),
            ("The Office (UK)", 2001, 14),
            ("Parks and Recreation", 2009, 125),
        ],
    )
    conn.commit()
    conn.close()

    previous = os.getcwd()
    os.chdir(workdir)
    try:
        import app as app_module
    finally:
        os.chdir(previous)
    return app_module


@pytest.fixture
def client(app_module):
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()
