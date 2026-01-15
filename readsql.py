import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")
df = pd.read_sql("SELECT * FROM pv_data", conn)
print(df)
