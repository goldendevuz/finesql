import shutil
from pathlib import Path

import pytest

from finesql import Table, Column, ForeignKey
from finesql.orm import Database


STORAGES_DIR = Path("../storages")
DB_FILENAME = "test.db"
DB_PATH = STORAGES_DIR / DB_FILENAME


def _clean_storages_dir() -> None:
    """Remove everything inside storages/ (files and subdirs)."""
    if not STORAGES_DIR.exists():
        return
    for entry in STORAGES_DIR.iterdir():
        try:
            if entry.is_file() or entry.is_symlink():
                entry.unlink()
            elif entry.is_dir():
                shutil.rmtree(entry)
        except Exception:
            pass


# ---------- Author/Book fixtures ----------

@pytest.fixture
def author():
    class Author(Table):
        name = Column(str)
        age = Column(int)
    return Author


@pytest.fixture
def book(author):
    class Book(Table):
        title = Column(str)
        published = Column(bool, default=False)
        author = ForeignKey(author)
    return Book


# ---------- Unified User/Post fixtures ----------

@pytest.fixture
def user():
    class User(Table):
        username = Column(str)
        age = Column(int, default=None)      # used in test_full_example
        email = Column(str, default=None)    # used in test_blog_system
    return User


@pytest.fixture
def post(user):
    class Post(Table):
        title = Column(str)
        body = Column(str, default=None)      # used in test_full_example
        content = Column(str, default=None)   # used in test_blog_system
        author = ForeignKey(user)
    return Post


# ---------- Hero fixture ----------

@pytest.fixture
def hero():
    class Hero(Table):
        name = Column(str)
        secret_name = Column(str)
        age = Column(int, default=None)
    return Hero


# ---------- Todo fixture ----------

@pytest.fixture
def todo():
    class Todo(Table):
        title = Column(str)
        completed = Column(bool, default=False)
        priority = Column(int)
    return Todo


# ---------- Database fixture ----------

@pytest.fixture
def db():
    """
    Function-scoped DB fixture:
    - Ensures ./storages exists
    - Cleans previous contents
    - Creates a fresh Database instance
    - Yields the Database to the test
    - Cleans up afterwards
    """
    STORAGES_DIR.mkdir(parents=True, exist_ok=True)
    _clean_storages_dir()

    db = Database(str(DB_PATH))
    yield db

    try:
        if hasattr(db, "close") and callable(db.close):
            db.close()
        elif hasattr(db, "conn"):
            db.conn.close()
    except Exception:
        pass

    _clean_storages_dir()
