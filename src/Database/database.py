from sqlalchemy import text
from Config.config import engine , MYSQL_DATABASE



class DataBase : 
    def __init__(self):
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT DATABASE();"))
                print(f"✅ Connected to database: {result.fetchone()[0]}")
        except Exception as e:
            print(f"❌ Error connecting to MySQL: {e}")


    def get_schema(self):
        query = """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = :database;
        """
        with engine.connect() as connection:
            result = connection.execute(text(query), {"database": MYSQL_DATABASE})
            rows = result.fetchall()

        schema = {}
        for table, column, dtype in rows:
            schema.setdefault(table, []).append(f"{column} ({dtype})")

        return schema