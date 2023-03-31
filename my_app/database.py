import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

database_uri = os.environ.get('DATABASE_URL')

def get_conn():
    conn = psycopg2.connect(
        database_uri
        )
    
    return conn
