# FineSQL ORM

![Finesql](https://img.shields.io/badge/finesql-0.1.1-red)
![Purpose](https://img.shields.io/badge/purpose-learning-green.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

FineSQL is a lightweight Python ORM built on top of `sqlite3` for educational purposes.  
It provides simple table definitions, CRUD operations, and foreign key support while keeping the codebase minimal and easy to understand.

---

## Installation

No external dependencies required — only Python standard library.

```bash
git clone https://github.com/goldendevuz/finesql
cd finesql
```

---

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
user = User(username="Alice", age=25)
db.save(user)

post = Post(title="Hello World", body="This is my first post", author=user)
db.save(post)
```

### 4. Query Records

```python
# Get all users
users = db.all(User)
for u in users:
    print(u.id, u.username, u.age)

# Get by id
alice = db.get(User, id=1)
print(alice.username)

# Filter by field (LIKE search)
maybe_alice = db.get_by_field(User, field_name="username", value="Alice")
print(maybe_alice.username)

# Custom select (dict result)
result = db.get_user(User, field_name="username", value="Alice", return_fields=["id", "age"])
print(result)  # {'id': 1, 'age': 25}
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

---

## Relationships

Foreign keys can be defined using `ForeignKey`.  
For example, `Post` has an `author = ForeignKey(User)`.  
When fetching posts, the related `User` instance will be automatically resolved:

```python
post = db.get(Post, id=1)
print(post.author.username)
```

## Full Example

Here’s the complete example code in one file:

```python
from finesql import Database, Table, Column, ForeignKey

# Define models
class User(Table):
    username = Column(str)
    age = Column(int)

class Post(Table):
    title = Column(str)
    body = Column(str)
    author = ForeignKey(User)

# Initialize database
db = Database("app.db")
db.create(User)
db.create(Post)

# Create records
user = User(username="Alice", age=25)
db.save(user)
post = Post(title="Hello World", body="This is my first post", author=user)
db.save(post)

# Query records
print("All users:", db.all(User))
print("User by id:", db.get(User, id=1).username)

# Update
alice = db.get(User, id=1)
alice.age = 26
db.update(alice)

# Relationship
post = db.get(Post, id=1)
print("Post author:", post.author.username)

# Delete
db.delete(User, id=1)
```

---

## API Reference

### `Database`
- `create(table)` → Creates a table.
- `save(instance)` → Inserts a record.
- `all(table)` → Returns all records.
- `get(table, id)` → Get record by id.
- `get_by_field(table, field_name, value)` → LIKE search by field.
- `get_user(table, field_name, value, return_fields)` → Dict select with custom fields.
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