import os
import glob
import sqlite3

import pytest
from icecream import ic

# Clean storages dir before all tests
for file in glob.glob("storages/*"):
    if os.path.isfile(file):
        os.remove(file)


def save_obj(db, table, **kwargs):
    obj = table(**kwargs)
    db.save(obj)
    return obj


def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_table_definition(author, book):
    assert author.name.type == str
    assert book.author.table == author

    assert author.name.sql_type == "TEXT"
    assert author.age.sql_type == "INTEGER"
    assert book.title.sql_type == "TEXT"


def test_table_creation(db, author, book):
    db.create(author)
    db.create(book)

    assert author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    assert book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ("author", "book"):
        assert table in db.tables


def test_table_instance_creation(db, author):
    db.create(author)
    john = author(name="John Doe", age=44)
    assert john.name == "John Doe"
    assert john.age == 44
    assert john.id is None


def test_save_save_table_instance(db, author):
    db.create(author)

    john = author(name="John Doe", age=44)
    db.save(john)
    assert john.id == 1

    jack = author(name="Jack Ma", age=55)
    db.save(jack)
    assert jack.id == 2


def test_query_all_authors(db, author):
    db.create(author)
    save_obj(db, author, name="John Doe", age=44)
    save_obj(db, author, name="Jack Ma", age=23)

    authors = db.all(author)
    assert len(authors) == 2
    assert {a.name for a in authors} == {"John Doe", "Jack Ma"}


def test_get_author(db, author):
    db.create(author)
    save_obj(db, author, name="John Doe", age=44)

    john = db.get(author, id=1)
    assert isinstance(john, author)
    assert john.id == 1
    assert john.name == "John Doe"
    assert john.age == 44


def test_get_book(db, author, book):
    db.create(author)
    db.create(book)

    john = save_obj(db, author, name="John Doe", age=44)
    jack = save_obj(db, author, name="Jack Ma", age=23)

    save_obj(db, book, title="Atomic Habits", published=False, author=john)
    book_2 = save_obj(db, book, title="Show your work", published=True, author=jack)

    assert book_2.title == "Show your work"
    assert book_2.author.name == "Jack Ma"


def test_update_author(db, author):
    db.create(author)
    john = save_obj(db, author, name="John Doe", age=23)

    john.age = 43
    john.name = "John Wick"
    db.update(john)

    updated = db.get(author, id=john.id)
    assert updated.name == "John Wick"
    assert updated.age == 43


def test_delete_author(db, author):
    db.create(author)
    john = save_obj(db, author, name="John Doe", age=23)

    db.delete(author, id=john.id)
    with pytest.raises(Exception):
        db.get(author, id=john.id)


def test_get_all_heroes(db, hero):
    db.create(hero)

    save_obj(db, hero, name="Deadpond", secret_name="Dive Wilson")
    save_obj(db, hero, name="Spider-Boy", secret_name="Pedro Parqueador")
    save_obj(db, hero, name="Rusty-Man", secret_name="Tommy Sharp", age=48)

    heroes = db.all(hero)
    assert len(heroes) == 3
    assert heroes[0].secret_name == "Dive Wilson"
    assert heroes[2].name == "Rusty-Man"
    assert heroes[2].age == 48


def test_get_hero(db, hero):
    db.create(hero)
    save_obj(db, hero, name="Deadpond", secret_name="Dive Wilson")
    save_obj(db, hero, name="Spider-Boy", secret_name="Pedro Parqueador")

    spidey = db.get(hero, id=2)
    assert spidey.name == "Spider-Boy"
    assert spidey.secret_name == "Pedro Parqueador"


def test_full_example(db, user, post):
    db.create(user)
    db.create(post)

    alice = save_obj(db, user, username="Alice", age=25)
    hello = save_obj(db, post, title="Hello World", body="This is my first post", author=alice)

    users = db.all(user)
    assert users[0].username == "Alice"
    assert db.get(user, id=1).username == "Alice"

    alice.age = 26
    db.update(alice)
    assert db.get(user, id=1).age == 26

    fetched_post = db.get(post, id=1)
    assert fetched_post.author.username == "Alice"

    db.delete(user, id=1)
    with pytest.raises(Exception):
        db.get(user, id=1)


def test_blog_system(db, user, post):
    db.create(user)
    db.create(post)

    alice = save_obj(db, user, username="alice", email="alice@blog.com")
    blog_post = save_obj(db, post, title="My First Post", content="Hello world!", author=alice)

    fetched_post = db.get(post, id=1)
    assert fetched_post.title == "My First Post"
    assert fetched_post.author.username == "alice"


def test_todo_app(db, todo):
    db.create(todo)

    task = save_obj(db, todo, title="Learn FineSQL", priority=1)
    assert task.completed is False

    task.completed = True
    db.update(task)
    updated = db.get(todo, id=1)
    assert bool(updated.completed)