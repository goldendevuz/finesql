import os

import pytest

from finesql.orm import Table, Column, ForeignKey, Database


@pytest.fixture
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author


@pytest.fixture
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    return Book


@pytest.fixture
def hero_v1():
    """Returns a Hero class without default age."""

    class Hero(Table):
        name = Column(str)
        secret_name = Column(str)
        age = Column(int)

    return Hero


@pytest.fixture
def hero_v2():
    """Returns a Hero class with default age."""

    class Hero(Table):
        name = Column(str)
        secret_name = Column(str)
        age = Column(int, default=20)

    return Hero


@pytest.fixture
def db():
    DB_PATH = "./test.db"
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    db = Database(DB_PATH)
    return db
