import sqlite3
import inspect


class Database:
    def __init__(self, path):
        self.conn = sqlite3.Connection(path)

    @property
    def tables(self):
        SELECT_TABLE_SQL = "SELECT name FROM sqlite_master WHERE type = 'table' ;"
        return [row[0] for row in self.conn.execute(SELECT_TABLE_SQL).fetchall()]

    def create(self, table):
        self.conn.execute(table._get_create_sql())

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        curser = self.conn.execute(sql, values)
        self.conn.commit()
        instance._data["id"] = curser.lastrowid

    def all(self, table):
        sql, fields = table._get_select_all_sql()

        result = []
        for row in self.conn.execute(sql).fetchall():
            instance = table()
            for field, value in zip(fields, row):
                if field.endswith("_id"):
                    field = field[:-3]
                    fk = getattr(table, field)
                    value = self.get(fk.table, id=value)
                setattr(instance, field, value)

            result.append(instance)

        return result

    def get_user(self, table, field_name=None, value=None, return_fields=None):
        if field_name is None and value is None:
            raise ValueError("Either 'field_name' and 'value' must be provided.")

        sql = table._get_select_by_user_sql(field_name=field_name, return_fields=return_fields)
        params = (value,)

        cursor = self.conn.execute(sql, params)
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]

        return dict(zip(columns, row))

    def get_by_field(self, table, field_name=None, value=None):

        if field_name is not None and value is not None:
            sql, fields = table._get_select_by_field_sql(field_name=field_name, value=value)
            params = (f"%{value}%",)
        else:
            raise ValueError("Either 'field_name' and 'value' must be provided.")

        row = self.conn.execute(sql, params).fetchone()

        if row is None:
            raise Exception(f"{table.__name__} instance not found")

        instance = table()

        for field, value in zip(fields, row):
            if field.endswith("_id"):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)

            setattr(instance, field, value)

        return instance

    def get(self, table, id):
        sql, fields = table._get_select_by_id_sql(id=id)
        row = self.conn.execute(sql).fetchone()

        if row is None:
            raise Exception(f"{table.__name__} instance with {id} does not exist")

        instance = table()
        for field, value in zip(fields, row):
            if field.endswith("_id"):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)
            setattr(instance, field, value)

        return instance

    def update(self, instance):
        sql, values = instance._get_update_sql()
        self.conn.execute(sql, values)
        self.conn.commit()

    def delete(self, table, id):
        sql = table._get_delete_sql(id)
        self.conn.execute(sql)
        self.conn.commit()


class Table:
    def __init__(self, **kwargs):
        self._data = {
            "id": None

        }

        for key, value in kwargs.items():
            self._data[key] = value

    @classmethod
    def _get_create_sql(cls):
        CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT"

        ]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(f"{name} {col.sql_type}")

            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id INTEGER")

        fields = ', '.join(fields)
        name = cls.__name__.lower()

        return CREATE_TABLE_SQL.format(name=name, fields=fields)

    def __getattribute__(self, attr_name):
        _data = super().__getattribute__("_data")

        if attr_name in _data:
            return _data[attr_name]

        return super().__getattribute__(attr_name)

    # overwrite setattr method
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name in self._data:
            self._data[name] = value

    def _get_insert_sql(self):
        INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, col in inspect.getmembers(cls):
            value = getattr(self, name)

            if isinstance(col, Column):
                fields.append(name)
                if not isinstance(value, Column):
                    values.append(value)
                else:
                    values.append(None)
                placeholders.append("?")
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")
                values.append(value.id)
                placeholders.append("?")

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)

        sql = INSERT_SQL.format(name=cls.__name__.lower(), fields=fields, placeholders=placeholders)

        return sql, values

    @classmethod
    def _get_select_all_sql(cls):
        SELECT_ALL_SQL = "SELECT {fields} FROM {name};"

        fields = ["id"]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")
        sql = SELECT_ALL_SQL.format(name=cls.__name__.lower(), fields=", ".join(fields))

        return sql, fields

    @classmethod
    def _get_select_by_id_sql(cls, id):
        SELECT_GET_SQL = "SELECT {fields} FROM {name} WHERE id = {id};"
        fields = ["id"]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")

        sql = SELECT_GET_SQL.format(name=cls.__name__.lower(), fields=", ".join(fields), id=id)

        return sql, fields

    @classmethod
    def _get_select_by_field_sql(cls, field_name, value):
        SELECT_GET_SQL_BY_FIELD = "SELECT {fields} FROM {name} WHERE {field_name} LIKE ?;"

        fields = ["id"]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id")

        sql = SELECT_GET_SQL_BY_FIELD.format(name=cls.__name__.lower(), fields=", ".join(fields), field_name=field_name)

        return sql, fields

    @classmethod
    def _get_select_by_user_sql(cls, field_name, return_fields=None):
        if return_fields is None:
            fields_str = "*"
        else:
            fields_str = ", ".join(return_fields)

        query = f"SELECT {fields_str} FROM {cls.__name__.lower()} WHERE {field_name} = ?"
        return query

    def _get_update_sql(self):
        fields = []
        values = []

        for name, col in inspect.getmembers(self.__class__):
            if isinstance(col, Column):
                fields.append(name)
                values.append(getattr(self, name))
            elif isinstance(col, ForeignKey):
                fk = getattr(self, name)
                fields.append(f"{name}_id")
                values.append(fk.id if fk else None)

        sql = f"UPDATE {self.__class__.__name__.lower()} SET {', '.join([f'{field} = ?' for field in fields])} WHERE id = ?;"
        values.append(self.id)

        return sql, values

    @classmethod
    def _get_delete_sql(cls, id):
        DELETE_SQL = "DELETE FROM {name} WHERE id = {id};"

        sql = DELETE_SQL.format(name=cls.__name__.lower(), id=id)

        return sql

    def __repr__(self):
        attrs = ", ".join(
            f"{field}={repr(value)}"
            for field, value in self.__dict__.items()
            if field != "_data"
        )
        return f"{self.__class__.__name__}({attrs})"


class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        SQLITE_TYPE_MAP = {
            int: "INTEGER",
            str: "TEXT",
            bool: "INTEGER",  # 0 OR 1
            float: "REAL",
            bytes: "BLOB"

        }
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table