import sqlite3
from collections.abc import Iterable

from pydantic import BaseModel

from auto_functions.logger import get_logger
from auto_functions.routes.api_specs.schemas import ApiSpec

table_models = [ApiSpec]


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect("auto_functions/data/app.db")
    conn.row_factory = sqlite3.Row
    return conn


def execute_sql(sql: str) -> None:
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        get_logger().exception("SQL error", exc_info=e)
    finally:
        conn.close()


def execute_sql_select(sql: str) -> Iterable[sqlite3.Row]:
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        for row in cursor:
            yield row
        conn.commit()
    except Exception as e:
        get_logger().exception("SQL error", exc_info=e)
    finally:
        conn.close()


def create_tables() -> None:
    for model in table_models:
        create_table(model, model.__name__.lower())


def create_table(model: type[BaseModel], table_name: str):
    columns: list[str] = []
    schema = model.model_json_schema()
    for field_name, field_type in get_all_annotations(model).items():
        if not schema["properties"][field_name].get("no_db"):
            columns.append(f"{field_name} {translate_type(field_type)}")
    columns_sql = ", ".join(columns)
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
    execute_sql(sql)


def get_all_annotations(model: type[BaseModel]) -> dict[str, type]:
    annotations: dict[str, type] = {}
    # Iterate over the MRO in reverse (excluding 'object')
    for cls in reversed(model.__mro__[:-1]):
        # Merge the annotations
        annotations.update(getattr(cls, "__annotations__", {}))
    return annotations


def translate_type(py_type: type):
    if py_type == str:
        return "TEXT"
    elif py_type == int:
        return "INTEGER"
    elif py_type == float:
        return "REAL"
    elif py_type == bool:
        return "BOOLEAN"
    # Add more translations as needed
    return "TEXT"
