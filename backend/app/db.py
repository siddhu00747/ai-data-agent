# backend/app/db.py
import duckdb, os, json
DB_PATH = "backend/data/analytics.db"
conn = duckdb.connect(database=DB_PATH, read_only=False)
def register_table_from_df(table_name: str, df):
    # write dataframe into duckdb in-memory table
    conn.register(table_name, df)
def read_metadata(file_id: str):
    path = f"backend/data/{file_id}_meta.json"
    if not os.path.exists(path): return None
    return json.load(open(path))
def save_metadata(file_id: str, obj):
    path = f"backend/data/{file_id}_meta.json"
    json.dump(obj, open(path, "w"), default=str)
# export db handle for queries
db = conn
