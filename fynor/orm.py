import sqlite3

SQL_TYPES = {
    int: 'INTEGER',
    float: 'REAL',
    str: 'TEXT',
    bytes: 'BLOB',
    bool: 'INTEGER', # 0/1
}


class Database:
    def __init__(self, path):
        self.conn = sqlite3.Connection(path)

    @property
    def tables(self):
        return []

class Table:
    pass

class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        return SQL_TYPES[self.type]

class ForeignKey:
    def __init__(self, table):
        self.table = table