import sqlite3, os
from typing import Optional, Any, List
from src.roles import Role
from src.lib import Logger
from src.utils import sqliteutils
from config import Config

config = Config()


class DatabaseManager:
    def __init__(self, db_name: str):
        self.schema = config.schema
        self.logger = Logger(self.__class__.__name__)

        db_path = os.path.abspath("instance/" + db_name + ".db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

        self.create_all()

    def create_all(self):
        for table in self.schema["tables"]:
            table_name = table["name"]
            if not self.table_exists(table_name):
                column_def = sqliteutils.get_column_def(table["columns"])
                foreign_key_def = sqliteutils.get_foreign_key_def(table["foreign_keys"]) if "foreign_keys" in table else None
                self.create_table(table_name, column_def, foreign_key_def)
                if table_name in self.schema["defaults"]:
                    for row in self.schema["defaults"][table_name]:
                        for column in table["columns"]:
                            if "default_function" in column:
                                function = sqliteutils.lookup_default_function(column["default_function"][0], globals())
                                args = column["default_function"][1:]
                                if all(arg is None for arg in args):
                                    row[column["column_name"]] = function()
                                else:
                                    row[column["column_name"]] = function(*args)
                        self.add_row(table_name, row)

    def close(self):
        self.connection.close()

    # Create #
    def create_table(self, table_name: str, column_def: str, foreign_key_def: str = None):
        command = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_def})"
        if foreign_key_def is not None:
            command += ", {}".format(foreign_key_def)
        self.cursor.execute(command)
        self.connection.commit()

    def add_row(self, table_name: str, column_values: dict):
        columns = ", ".join(column_values.keys())
        placeholders = ", ".join([":" + key for key in column_values.keys()])
        command = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(command, column_values)
        self.connection.commit()

    def add_user(self, column_values: dict):
        self.add_row("users", column_values)
        self.logger.log(f"Added user '{column_values['client_id']}': (name={column_values['usernames']}, roles={column_values['roles']})")

    # Read #
    def table_exists(self, table_name: str) -> bool:
        command = f"SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?"
        args = [(table_name,)]
        self.cursor.execute(command, *args)
        return True if self.cursor.fetchone() is not None else False

    def user_exists(self, client_id: str) -> bool:
        command = "SELECT * FROM users WHERE client_id = ?"
        args = [(client_id,)]
        self.cursor.execute(command, *args)
        return True if self.cursor.fetchone() is not None else False

    def get_user_column(self, client_id: str, column_name: str) -> Optional[Any]:
        if self.user_exists(client_id):
            command = f"SELECT {column_name} FROM users WHERE client_id = ?"
            args = [(client_id,)]
            self.cursor.execute(command, *args)
        else:
            raise KeyError(f"User with client_id '{client_id}' does not exist")
        result = self.cursor.fetchone()
        return result[0] if result is not None else None

    def get_user_latest_username(self, client_id: str) -> str:
        usernames = self.get_user_column(client_id, "usernames")
        return usernames.split("\0")[-1]

    def get_user_roles(self, client_id: str) -> Optional[List[Role]]:
        result = self.get_user_column(client_id, "roles")
        return [Role.from_name(role) for role in result.split(",")] if result is not None else None

    # Update #
    def update_user(self, client_id: str, column_values: dict):
        command = f"UPDATE users SET {', '.join([f'{column} = ?' for column in column_values])} WHERE client_id = ?"
        args = list(column_values.values()) + [client_id]
        self.cursor.execute(command, args)
        self.connection.commit()
        self.logger.log(f"Updated user '{client_id}': ({', '.join(['{}={}'.format(key, value) for key, value in column_values.items()])})")

    # Delete #
    def drop_table(self, table_name: str):
        command = f"DROP TABLE {table_name}"
        self.cursor.execute(command)
        self.connection.commit()
