"""Load the cleaned CSV into SQLite, run every named query in sql/queries.sql,
and export each result to data/processed/sql_<name>.csv (handy for Power BI)."""
import re, sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
con = sqlite3.connect(ROOT / "data" / "retail.db")
pd.read_csv(ROOT / "data" / "processed" / "sales_clean.csv").to_sql("sales", con, if_exists="replace", index=False)

text = (ROOT / "sql" / "queries.sql").read_text()
blocks = re.split(r"-- name: (\w+)[^\n]*\n", text)[1:]
for name, sql in zip(blocks[::2], blocks[1::2]):
    out = pd.read_sql_query(sql, con)
    out.to_csv(ROOT / "data" / "processed" / f"sql_{name}.csv", index=False)
    print(f"\n=== {name} ({len(out)} rows) ===")
    print(out.head(8).to_string(index=False))
con.close()
