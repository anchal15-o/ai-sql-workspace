from sqlalchemy import inspect


def get_schema_info(engine):
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    schema_data = []

    for table_name in tables:
        columns = inspector.get_columns(table_name)

        schema_data.append({
            "table_name": table_name,
            "columns": [
                {
                    "name": column["name"],
                    "type": str(column["type"])
                }
                for column in columns
            ]
        })

    return schema_data