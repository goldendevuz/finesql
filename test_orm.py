import os
import sqlite3

import pytest
from icecream import ic

from fynor.orm import Database

def save_obj(db, Table, **kwargs):
    obj = Table(**kwargs)
    db.save(obj)

    return obj


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
    ic(46000000000000000000000)
    db.create(Author)

    name = "John Doe"
    age = 44
    john = Author(name=name, age=age)
    ic(46000000000000000000001)

    assert john.name == name
    assert john.age == age
    assert john.id is None

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

def test_query_all_authors(db, Author):
    db.create(Author)

    john = save_obj(db, Author, name="John Doe", age=44)
    jack = save_obj(db, Author, name="Jack Ma", age=23)

    authors = db.all(Author)

    assert Author._get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", "name"],
    )
    assert len(authors) == 2

    for id, author in enumerate(authors):
        assert isinstance(authors[id], Author)
        assert author.age in {44, 23}
        assert author.name in {"John Doe", "Jack Ma"}
        assert author.id in {1, 2}

    jack = Author(name='Jack Ma', age=55)
    db.save(jack)

def test_gdt_author(db, Author):
    db.create(Author)

    save_obj(db, Author, name="John Doe", age=44)

    john = db.get(Author, id=1)

    assert Author._get_select_by_id_sql(id=1) == (
        "SELECT id, age, name FROM author WHERE id=1;",
        ["id", "age", "name"],
    )
    assert isinstance(john, Author)
    assert john.id == 1
    assert john.age == 44
    assert john.name == "John Doe"

def test_get_book(db, Author, Book):
    db.create(Author)
    db.create(Book)

    john = save_obj(db, Author, name="John Doe", age=44)
    jack = save_obj(db, Author, name="Jack Ma", age=23)

    book_1 = save_obj(db, Book, title="Atomic Habits", published=False, author=john)
    book_2 = save_obj(db, Book, title="Show your work", published=True, author=jack)

    book = db.get(Book, id=2)
    
    assert book.title == "Show your work"
    assert book.id == 2
    assert book.author.name == "Jack Ma"
    assert book.author.age == 23


def test_get_all_books(db, Author, Book):
    db.create(Author)
    db.create(Book)

    john = save_obj(db, Author, name="John Doe", age=44)
    jack = save_obj(db, Author, name="Jack Ma", age=23)

    book_1 = save_obj(db, Book, title="Atomic Habits", published=False, author=john)
    book_2 = save_obj(db, Book, title="Show your work", published=True, author=jack)

    books = db.all(Book)

    assert len(books) == 2
    assert books[1].author.name == "Jack Ma"


def test_update_author(db, Author):
    db.create(Author)

    john = save_obj(db, Author, name="John Doe", age=23)

    john.age = 43
    john.name = "John Wick"
    db.update(john)

    john = db.get(Author, id=john.id)

    assert john.name == "John Wick"
    assert john.age == 43


def test_delete_author(db, Author):
    db.create(Author)

    john = save_obj(db, Author, name="John Doe", age=23)

    db.delete(Author, id=1)

    with pytest.raises(Exception):
        db.get(Author, id=1)