import inspect
import sqlite3

from icecream import ic

SQL_TYPES = {
    int: 'INTEGER',
    float: 'REAL',
    str: 'TEXT',
    bytes: 'BLOB',
    bool: 'INTEGER',  # 0/1
}


class Database:
    def __init__(self, path):
        self.conn = sqlite3.Connection(path)

    @property
    def tables(self):
        SELECT_SQL_TABLES = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [row[0] for row in self.conn.execute(SELECT_SQL_TABLES).fetchall()]

    def create(self, table):
        ic()
        self.conn.execute(table._get_create_sql())
        ic()


class Table:
    def __init__(self, **kwargs):
        self._data = dict(kwargs)
        self._data.update(id=None)
        ic(self._data)

    @classmethod
    def _get_create_sql(cls):
        CREATE_SQL_TABLE = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT"
        ]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(f"{name} {col.sql_type}")
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id INTEGER")

        fields = ", ".join(fields)
        name = cls.__name__.lower()

        query = CREATE_SQL_TABLE.format(name=name, fields=fields)
        return query

    def __getattribute__(self, name):
        _data = super().__getattribute__("_data")

        if name in _data:
            ic()
            return _data[name]
        return super().__getattribute__(name)



class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        return SQL_TYPES[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table
