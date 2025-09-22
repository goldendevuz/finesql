# FineSQL ORM

![FineSQL](https://img.shields.io/badge/FineSQL-0.0.1-red?style=for-the-badge)
![pytest](https://img.shields.io/badge/pytest-8.4.2-blue?style=for-the-badge)
![icecream](https://img.shields.io/badge/icecream-2.1.8-orange?style=for-the-badge)
![Purpose](https://img.shields.io/badge/purpose-learning-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)

FineSQL is a lightweight Python ORM built on top of `sqlite3` for educational purposes.  
It provides simple table definitions, CRUD operations, and foreign key support while keeping the codebase minimal and easy to understand.

## Installation

<details>
<summary><b>pip</b></summary>

```bash
pip install finesql
```
</details>

<details>
<summary><b>uv</b></summary>

```bash
uv add finesql
```
</details>

## Quick Start

### 1. Define Tables

```python
from finesql import Database, Table, Column, ForeignKey

class User(Table):
    username = Column(str)
    age = Column(int)

class Post(Table):
    title = Column(str)
    body = Column(str)
    author = ForeignKey(User)
```

### 2. Initialize Database

```python
db = Database("app.db")

db.create(User)
db.create(Post)
```

### 3. Create Records

```python
# Create users
alice = User(full_name="Alice Johnson", age=25)
db.save(alice)

robert = User(full_name="Robert Smith", age=30)
db.save(robert)

# Create a post
post = Post(title="Hello World", body="This is my first post", author=robert)
db.save(post)
```

### 4. Query Records

```python
# Get all users
users = db.all(User)
print(users)

# Get by id
user1 = db.get(User, id=1)
print(user1)

# Filter by full_name (reuse first name)
alice = db.get_by_field(User, field_name="full_name", value="Alice Johnson")
print(alice)

robert = db.get_by_field(User, field_name="full_name", value="Robert Smith")
print(robert)
```

### 5. Update Records

```python
alice = db.get(User, id=1)
alice.age = 26
db.update(alice)
```

### 6. Delete Records

```python
db.delete(User, id=1)
```

## Relationships

Foreign keys can be defined using `ForeignKey`.  
For example, `Post` has an `author = ForeignKey(User)`.  
When fetching posts, the related `User` instance will be automatically resolved:

```python
post = db.get(Post, id=1)
print(post.author)
```

## API Reference

### `Database`
- `create(table)` → Creates a table.
- `save(instance)` → Inserts a record.
- `all(table)` → Returns all records.
- `get(table, id)` → Get record by id.
- `get_by_field(table, field_name, value)` → LIKE search by field.
- `update(instance)` → Updates a record.
- `delete(table, id)` → Deletes a record.

### `Table`
- Base class for all models.
- Automatically provides `id` field.
- Column and ForeignKey definitions supported.

### `Column`
- Define a typed column (`int`, `str`, `float`, `bool`, `bytes`).

### `ForeignKey`
- Define foreign key to another table.

---

## Roadmap

- [ ] Migrations
- [ ] Query builder
- [ ] Async support
- [ ] Type checking with `mypy`

---

## License

MIT © 2025 Abdulmajid Yunus

---