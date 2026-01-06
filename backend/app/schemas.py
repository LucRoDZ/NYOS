from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    analysis: Optional[dict] = None


class BatchCreate(BaseModel):
    batch_id: str
    product_name: str
    manufacturing_date: datetime
    machine: str
    operator: str
    compression_force: float
    hardness: float
    weight: float
    thickness: float
    yield_percent: float
    status: str = "released"


class BatchResponse(BaseModel):
    id: int
    batch_id: str
    product_name: str
    manufacturing_date: datetime
    machine: str
    hardness: float
    yield_percent: float
    status: str

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_batches: int
    batches_this_month: int
    avg_yield: float
    complaints_open: int
    capas_open: int
    equipment_due: int
    trend_alert: Optional[str] = None


class TrendData(BaseModel):
    dates: List[str]
    values: List[float]
    parameter: str
    trend_direction: str
    alert: bool


class UploadResponse(BaseModel):
    filename: str
    records_imported: int
    data_type: str
