import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\DEVINSTANCE;"
    "DATABASE=Superclinic;"
    "Trusted_Connection=yes;"
)