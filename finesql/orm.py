import inspect
import sqlite3

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
        self.conn.execute(table._get_create_sql())

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        cursor = self.conn.execute(sql, values)
        self.conn.commit()
        instance._data["id"] = cursor.lastrowid

    def all(self, table):
        query, fields = table._get_select_all_sql()

        result = []
        for row in self.conn.execute(query).fetchall():
            instance = table()
            for field, value in zip(fields, row):
                if field.endswith("_id"):
                    field = field[:-3]
                    fk = getattr(table, field)
                    value = self.get(fk.table, id=value)
                setattr(instance, field, value)
            result.append(instance)
        return result

    def get(self, table, id):
        query, fields = table._get_select_by_id_sql(id=id)

        row = self.conn.execute(query).fetchone()

        if row is None:
            raise Exception(f"{table.__name__} instance with id {id} does not exist")

        instance = table()
        for field, value in zip(fields, row):
            if field.endswith("_id"):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)
            setattr(instance, field, value)

        return instance

    def update(self, instance):
        query, values = instance._get_update_sql()
        self.conn.execute(query, values)
        self.conn.commit()

    def delete(self, table, id):
        query = table._get_delete_sql(id=id)
        self.conn.execute(query)
        self.conn.commit()


class Table:
    def __init__(self, **kwargs):
        self._data = {"id": None}

        for key, value in kwargs.items():
            self._data[key] = value

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

    def _get_insert_sql(self):
        INSERT_QUERY = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, col in inspect.getmembers(cls):
            def _():
                placeholders.append("?")

            if isinstance(col, Column):
                fields.append(name)
                values.append(getattr(self, name))
                _()
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")
                values.append(getattr(self, name).id)
                _()

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)

        sql = INSERT_QUERY.format(name=cls.__name__.lower(), fields=fields, placeholders=placeholders)
        return sql, values


    def __getattribute__(self, name):
        _data = super().__getattribute__("_data")

        if name in _data:
            return _data[name]
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if name in self._data:
            self._data[name] = value

    @classmethod
    def _get_select_all_sql(cls):
        SELECT_ALL_QUERY = "SELECT {fields} FROM {name};"

        fields = ["id"]
        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")

        query = SELECT_ALL_QUERY.format(fields=", ".join(fields), name=cls.__name__.lower())
        return query, fields

    @classmethod
    def _get_select_by_id_sql(cls, id):
        SELECT_ALL_QUERY = "SELECT {fields} FROM {name} WHERE id={id};"

        fields = ["id"]
        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")

        query = SELECT_ALL_QUERY.format(fields=", ".join(fields), name=cls.__name__.lower(), id=id)
        return query, fields

    def _get_update_sql(self):
        UPDATE_QUERY = "UPDATE {name} SET {fields} WHERE id={id};"
        cls = self.__class__
        fields = []
        values = []

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
                values.append(getattr(self, name))
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")
                values.append(getattr(self, name).id)

        query = UPDATE_QUERY.format(
            name=cls.__name__.lower(), 
            fields=", ".join([f"{field} = ?" for field in fields]),
            id=self.id
        )
        return query, values

    @classmethod
    def _get_delete_sql(cls, id):
        DELETE_QUERY = "DELETE FROM {name} WHERE id={id};"
        query = DELETE_QUERY.format(name=cls.__name__.lower(), id=id)
        return query

class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        return SQL_TYPES[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table
