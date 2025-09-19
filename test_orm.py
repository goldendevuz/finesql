import os
import sqlite3

import pytest
from icecream import ic

from fynor.orm import Database





def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_table_definition(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"
    assert Book.title.sql_type == "TEXT"
    # TODO assert Book.published.sql_type == "ODOT"
    # TODO assert Book.author.sql_type == "ODOT"


def test_table_creation(db, Author, Book):
    db.create(Author)
    db.create(Book)

    assert Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    assert Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ("author", "book"):
        assert table in db.tables

def test_table_instance_creation(db, Author):
    db.create(Author)

    name = "John Doe"
    age = 44
    john = Author(name=name, age=age)

    assert john.name == name
    assert john.age == age
    assert john.id is None

    """"""

def test_save_save_table_instance(db, Author):
    db.create(Author)

    name = "John Doe"
    age = 44
    john = Author(name=name, age=age)
    db.save(john)

    assert john._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [age, name],
    )
    assert john.id == 1

    jack = Author(name='Jack Ma', age=55)
    db.save(jack)
    assert jack.id == 2