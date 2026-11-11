import pandas as pd
from sqlalchemy import create_engine, text, inspect
from app.config import settings

class DBConnector:

    def __init__(self, connection_url: str = None):
        self.connection_url =connection_url or settings.database_url
        self.engine = None 

    def connect(self):
        try:
            self.engine = create_engine(self.connection_url)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Успешное подключение к базе данных!")
            return True
            
        except Exception as e:
             print(f"Ошибка подключения: {e}")
             return False

    def get_tables(self):
        if not self.engine:
            self.connect()

        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            return tables
        except Exception as e:
            print(f"Ошибка при получении списка таблиц: {e}")
            return []

    def read_table(self, table_name: str, limit: int = None) -> pd.DataFrame:
        if not self.engine:
            self.connect()
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"Ошибка при чтении таблицы {table_name}: {e}")
            return pd.DataFrame()