# backend/app/schema_models.py
from pydantic import BaseModel
from typing import List, Any
class ColumnMeta(BaseModel):
    name: str
    dtype: str
    missing_pct: float
    sample: List[Any]
class SheetMeta(BaseModel):
    table_name: str
    rows: int
    columns: List[ColumnMeta]
