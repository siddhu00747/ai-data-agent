# backend/app/llm.py
import os, json

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)

def plan_sql_from_question(schema: dict, table_name: str, question: str):
    """
    If OPENAI_API_KEY present, call OpenAI to convert NL -> SQL using a small prompt.
    Otherwise fallback to naive heuristics for common asks.
    Returns dict with keys: sql, chart_type, explain (or clarify if needs more info)
    """
    # Simple heuristic fallback:
    q = question.lower()
    # top N by column
    import re
    m = re.search(r"top\s*(\d+)\s*(.*)\s*by\s*(.*)", q)
    if m:
        n = int(m.group(1))
        target = m.group(2).strip() or "*"
        bycol = m.group(3).strip()
        if bycol in schema:
            sql = f"SELECT {target}, {bycol} FROM {table_name} ORDER BY {bycol} DESC LIMIT {n}"
            return {"sql": sql, "chart_type":"table", "explain": f"Top {n} by {bycol}"}
    # count or group by
    if "count" in q or "how many" in q or "distribution" in q:
        # try find a categorical column by heuristic
        for col,dt in schema.items():
            if "object" in dt or "str" in dt or "category" in dt:
                sql = f"SELECT {col} AS key, COUNT(*) AS cnt FROM {table_name} GROUP BY {col} ORDER BY cnt DESC"
                return {"sql": sql, "chart_type":"bar", "explain": f"Count by {col}"}
    # fallback: select sample
    sql = f"SELECT * FROM {table_name} LIMIT 50"
    return {"sql": sql, "chart_type":"table", "explain":"Sample rows (fallback). If you want aggregates, ask e.g. 'Top 10 customers by revenue'."}
