from datetime import datetime


def get_column_def(columns: list) -> str:
    column_defs = []
    for column in columns:
        column_defs.append(format_column_def(**column))
    column_def = ", ".join(column_defs)
    return column_def


def format_column_def(column_name: str, column_type: str, **kwargs) -> str:
    column_constraints = []
    for key, value in kwargs.items():
        match key:
            case "primary_key":
                if value:
                    column_constraints.append("PRIMARY KEY")
            case "nullability":
                if not value:
                    column_constraints.append("NOT NULL")
            case "unique":
                if value:
                    column_constraints.append("UNIQUE")
            case "auto_increment":
                if value:
                    column_constraints.append("AUTOINCREMENT")

    column_constraint = " ".join(column_constraints)
    return "{0} {1} {2}".format(column_name, column_type, column_constraint).rstrip()


def get_foreign_key_def(foreign_keys: list) -> str:
    foreign_key_defs = []
    for foreign_key in foreign_keys:
        foreign_key_defs.append(format_foreign_key_def(**foreign_key))
    foreign_key_def = ", ".join(foreign_key_defs)
    return foreign_key_def


def format_foreign_key_def(child_key: str, parent_table: str, parent_key: str, **kwargs) -> str:
    clause_actions = []
    for key, value in kwargs.items():
        match key:
            case "on_update":
                clause_actions.append("ON UPDATE {}".format(value.upper()))
            case "on_delete":
                clause_actions.append("ON DELETE {}".format(value.upper()))
    action_clause = " ".join(clause_actions)
    return "FOREIGN KEY ({0}) REFERENCES {1} ({2}) {3}".format(child_key, parent_table, parent_key, action_clause).rstrip()


def datetime_to_string(datetime_object: datetime = datetime.utcnow()) -> str:
    return datetime_object.strftime("%Y-%m-%d %H:%M:%S")


def string_to_datetime(datetime_string: str) -> datetime:
    return datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")


def lookup_default_function(function_string: str, lookup_dict: dict) -> callable:
    function_source = function_string.split(".")
    function = lookup_dict[function_source.pop(0)]
    if len(function_source) > 0:
        attributes = dir(function)
        method_dict = {attr: getattr(function, attr) for attr in attributes if callable(getattr(function, attr))}
        return lookup_default_function(".".join(function_source), method_dict)
    else:
        return function
