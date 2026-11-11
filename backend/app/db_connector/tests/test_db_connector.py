import pandas as pd
import pytest
from app.loaders.db_connector import DBConnector

@pytest.fixture
def test_db():
    db = DBConnector(connection_url="sqlite:///:memory:")
    db.connect()
    
    from sqlalchemy import text 
    with db.engine.connect() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER, name TEXT)"))
        conn.execute(text("INSERT INTO users VALUES (1, 'Alise'), (2, 'Bob')"))
        conn.commit()
    return db

def test_get_tables(test_db):
    tables = test_db.get_tables()
    assert 'users' in tables
    
def test_read_table(test_db):
    df = test_db.read_table('users')
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.iloc[0]['name'] == 'Alise'