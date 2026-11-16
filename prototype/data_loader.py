import pandas as pd
from sqlalchemy import create_engine

class DataLoader:
    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        print(f" Reading CSV: {file_path}")
        # sep=None заставит Pandas автоматически определить, запятая там или точка с запятой
        return pd.read_csv(file_path, sep=None, engine='python', encoding='utf-8-sig')

    @staticmethod
    def load_from_db(connection_string: str, query: str) -> pd.DataFrame:
        print(f" Connecting to Database...")
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            return pd.read_sql(query, conn)