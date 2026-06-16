import pyodbc
from dotenv import load_dotenv
import os

load_dotenv()


def get_pos_connection():
    conn = pyodbc.connect(
        f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={os.getenv('POS_DB_SERVER')};
        DATABASE={os.getenv('POS_DB_NAME')};
        UID={os.getenv('POS_DB_USER')};
        PWD={os.getenv('POS_DB_PASSWORD')};
        TrustServerCertificate=yes;
        """
    )
    return conn


def get_bier_connection():
    conn = pyodbc.connect(
        f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={os.getenv('BIER_DB_SERVER')};
        DATABASE={os.getenv('BIER_DB_NAME')};
        UID={os.getenv('BIER_DB_USER')};
        PWD={os.getenv('BIER_DB_PASSWORD')};
        TrustServerCertificate=yes;
        """
    )
    return conn