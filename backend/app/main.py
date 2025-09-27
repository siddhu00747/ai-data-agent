# backend/app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd, os, uuid, json, re
from .db import db, register_table_from_df, read_metadata, save_metadata
from .llm import plan_sql_from_question

DATA_DIR = "backend/data"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="AI Data Agent - Backend")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/upload")
async def upload_excel(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())[:8]
    filename = f"{file_id}_{file.filename}"
    path = os.path.join(DATA_DIR, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    # read all sheets
    try:
        xls = pd.read_excel(path, sheet_name=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read Excel: {e}")
    metadata = {}
    for sheet_name, df in xls.items():
        # normalize columns
        df = df.copy()
        df.columns = [str(c).strip() if str(c).strip() != "" else f"col_{i+1}"
                      for i, c in enumerate(df.columns)]
        # attempt to coerce types (quick pass)
        for col in df.columns:
            # try datetime
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except: pass
            # try numeric
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except: pass
        table_name = f"t_{file_id}_{re.sub(r'\\W+', '_', sheet_name)}"
        register_table_from_df(table_name, df)
        col_meta = []
        for col in df.columns:
            sample = df[col].dropna().astype(str).head(5).tolist()
            col_meta.append({"name": col, "dtype": str(df[col].dtype), "missing_pct": float(df[col].isna().mean()), "sample": sample})
        metadata[sheet_name] = {"table_name": table_name, "rows": int(len(df)), "columns": col_meta}
    meta_path = os.path.join(DATA_DIR, f"{file_id}_meta.json")
    save_metadata(file_id, {"filename": file.filename, "path": path, "sheets": metadata})
    return {"file_id": file_id, "filename": file.filename, "sheets": list(metadata.keys()), "metadata": metadata}

class QueryRequest(BaseModel):
    file_id: str
    sheet_name: str
    question: str

@app.post("/query")
async def query(req: QueryRequest):
    meta = read_metadata(req.file_id)
    if not meta:
        raise HTTPException(404, "file_id not found")
    sheets = meta.get("sheets", {})
    if req.sheet_name not in sheets:
        raise HTTPException(404, "sheet not found")
    table_name = sheets[req.sheet_name]["table_name"]
    schema = {c['name']: c['dtype'] for c in sheets[req.sheet_name]['columns']}
    # Ask LLM to plan SQL (or use fallback)
    plan = plan_sql_from_question(schema, table_name, req.question)
    sql = plan.get("sql")
    chart_type = plan.get("chart_type", "table")
    explain = plan.get("explain", "")
    if not sql:
        return {"error": "Could not generate SQL. LLM asked for clarification.", "clarify": plan.get("clarify")}
    # Safety checks
    if re.search(r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|SYSTEM)\b", sql, re.IGNORECASE):
        raise HTTPException(400, "Unsafe SQL detected")
    # Limit rows
    if not re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
        sql = sql.rstrip(";") + " LIMIT 10000"
    try:
        df = db.execute(sql).df()
    except Exception as e:
        return {"error": f"SQL execution error: {e}", "sql": sql}
    # Prepare simple chart payload if possible
    chart = None
    if chart_type in ("bar","line","pie") and df.shape[1] >= 2:
        # naive: first two cols used
        chart = {"x": df.iloc[:,0].astype(str).tolist(), "y": df.iloc[:,1].tolist(), "series_name": df.columns[1]}
    return {"sql": sql, "explain": explain, "chart_type": chart_type, "chart": chart,
            "table": {"columns": df.columns.tolist(), "rows": df.head(200).to_dict(orient="records")}}

@app.get("/metadata/{file_id}")
def metadata(file_id: str):
    meta = read_metadata(file_id)
    if not meta:
        raise HTTPException(404, "file_id not found")
    return meta
