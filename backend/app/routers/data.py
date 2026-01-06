from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app import models
from app.schemas import DashboardStats, BatchResponse, UploadResponse
from app.services.gemini_service import analyze_trends
from datetime import datetime, timedelta
import pandas as pd
import io

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: Session = Depends(get_db)):
    total_batches = db.query(models.Batch).count()
    month_ago = datetime.utcnow() - timedelta(days=30)
    batches_month = (
        db.query(models.Batch)
        .filter(models.Batch.manufacturing_date >= month_ago)
        .count()
    )
    avg_yield = db.query(func.avg(models.Batch.yield_percent)).scalar() or 0
    complaints_open = (
        db.query(models.Complaint).filter(models.Complaint.status == "open").count()
    )
    capas_open = db.query(models.CAPA).filter(models.CAPA.status == "open").count()
    equipment_due = (
        db.query(models.Equipment)
        .filter(
            models.Equipment.next_calibration <= datetime.utcnow() + timedelta(days=7)
        )
        .count()
    )

    return DashboardStats(
        total_batches=total_batches,
        batches_this_month=batches_month,
        avg_yield=round(avg_yield, 2),
        complaints_open=complaints_open,
        capas_open=capas_open,
        equipment_due=equipment_due,
    )


@router.get("/batches")
async def get_batches(db: Session = Depends(get_db), limit: int = 100, offset: int = 0):
    batches = (
        db.query(models.Batch)
        .order_by(models.Batch.manufacturing_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return batches


@router.get("/trends/{parameter}")
async def get_trends(parameter: str, days: int = 30, db: Session = Depends(get_db)):
    valid_params = [
        "hardness",
        "yield_percent",
        "compression_force",
        "weight",
        "thickness",
    ]
    if parameter not in valid_params:
        raise HTTPException(
            status_code=400, detail=f"Paramètre invalide. Valides: {valid_params}"
        )
    return await analyze_trends(db, parameter, days)


@router.get("/complaints")
async def get_complaints(db: Session = Depends(get_db), status: str = None):
    query = db.query(models.Complaint)
    if status:
        query = query.filter(models.Complaint.status == status)
    return query.order_by(models.Complaint.date.desc()).all()


@router.get("/capas")
async def get_capas(db: Session = Depends(get_db), status: str = None):
    query = db.query(models.CAPA)
    if status:
        query = query.filter(models.CAPA.status == status)
    return query.order_by(models.CAPA.date.desc()).all()


@router.post("/upload", response_model=UploadResponse)
async def upload_data(
    file: UploadFile = File(...),
    data_type: str = "batch",
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400, detail="Seuls les fichiers CSV sont acceptés"
        )

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    records_count = 0

    if data_type == "batch":
        for _, row in df.iterrows():
            batch_id = row.get("batch_id", f"BATCH-{records_count}")
            existing = (
                db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
            )
            if existing:
                existing.product_name = row.get("product_name", "Paracetamol 500mg")
                existing.manufacturing_date = pd.to_datetime(
                    row.get("manufacturing_date", datetime.utcnow())
                )
                existing.machine = row.get(
                    "machine", row.get("tablet_press", "Unknown")
                )
                existing.operator = row.get("operator", "Unknown")
                existing.compression_force = float(
                    row.get("compression_force", row.get("main_compression_force", 0))
                )
                existing.hardness = float(
                    row.get("hardness", row.get("ipc_hardness_mean", 0))
                )
                existing.weight = float(
                    row.get("weight", row.get("ipc_weight_mean", 0))
                )
                existing.thickness = float(
                    row.get("thickness", row.get("ipc_thickness_mean", 0))
                )
                existing.yield_percent = float(
                    row.get("yield_percent", row.get("yield_percentage", 98))
                )
                existing.status = row.get("status", "released")
            else:
                batch = models.Batch(
                    batch_id=batch_id,
                    product_name=row.get("product_name", "Paracetamol 500mg"),
                    manufacturing_date=pd.to_datetime(
                        row.get("manufacturing_date", datetime.utcnow())
                    ),
                    machine=row.get("machine", row.get("tablet_press", "Unknown")),
                    operator=row.get("operator", "Unknown"),
                    compression_force=float(
                        row.get(
                            "compression_force", row.get("main_compression_force", 0)
                        )
                    ),
                    hardness=float(
                        row.get("hardness", row.get("ipc_hardness_mean", 0))
                    ),
                    weight=float(row.get("weight", row.get("ipc_weight_mean", 0))),
                    thickness=float(
                        row.get("thickness", row.get("ipc_thickness_mean", 0))
                    ),
                    yield_percent=float(
                        row.get("yield_percent", row.get("yield_percentage", 98))
                    ),
                    status=row.get("status", "released"),
                )
                db.add(batch)
            records_count += 1

    elif data_type == "qc":
        for _, row in df.iterrows():
            qc = models.QCResult(
                batch_id=row.get("batch_id"),
                test_date=pd.to_datetime(
                    row.get("test_date", row.get("testing_date", datetime.utcnow()))
                ),
                dissolution=float(
                    row.get("dissolution", row.get("dissolution_mean", 0))
                ),
                assay=float(row.get("assay", row.get("assay_result", 0))),
                hardness=float(row.get("hardness", row.get("hardness_result", 0))),
                friability=float(
                    row.get("friability", row.get("friability_result", 0))
                ),
                disintegration=float(
                    row.get("disintegration", row.get("disintegration_time", 0))
                ),
                uniformity=float(
                    row.get("uniformity", row.get("content_uniformity_rsd", 0))
                ),
                result=row.get("result", row.get("overall_result", "pass")),
            )
            db.add(qc)
            records_count += 1

    elif data_type == "complaint":
        for _, row in df.iterrows():
            complaint_id = row.get("complaint_id", f"CMP-{records_count}")
            existing = (
                db.query(models.Complaint)
                .filter(models.Complaint.complaint_id == complaint_id)
                .first()
            )
            if existing:
                existing.date = pd.to_datetime(
                    row.get("date", row.get("complaint_date", datetime.utcnow()))
                )
                existing.batch_id = row.get("batch_id", row.get("implicated_batch"))
                existing.category = row.get(
                    "category", row.get("complaint_category", "Unknown")
                )
                existing.severity = row.get(
                    "severity", row.get("severity_level", "low")
                )
                existing.description = row.get(
                    "description", row.get("complaint_description", "")
                )
                existing.status = row.get("status", "open")
            else:
                complaint = models.Complaint(
                    complaint_id=complaint_id,
                    date=pd.to_datetime(
                        row.get("date", row.get("complaint_date", datetime.utcnow()))
                    ),
                    batch_id=row.get("batch_id", row.get("implicated_batch")),
                    category=row.get(
                        "category", row.get("complaint_category", "Unknown")
                    ),
                    severity=row.get("severity", row.get("severity_level", "low")),
                    description=row.get(
                        "description", row.get("complaint_description", "")
                    ),
                    status=row.get("status", "open"),
                )
                db.add(complaint)
            records_count += 1

    elif data_type == "capa":
        for _, row in df.iterrows():
            capa_id = row.get("capa_id", f"CAPA-{records_count}")
            existing = (
                db.query(models.CAPA).filter(models.CAPA.capa_id == capa_id).first()
            )
            if existing:
                existing.date = pd.to_datetime(
                    row.get("date", row.get("initiation_date", datetime.utcnow()))
                )
                existing.type = row.get("type", row.get("capa_type", "corrective"))
                existing.source = row.get("source", row.get("source_type", "Unknown"))
                existing.description = row.get("description", "")
                existing.root_cause = row.get("root_cause", "")
                existing.status = row.get("status", "open")
            else:
                capa = models.CAPA(
                    capa_id=capa_id,
                    date=pd.to_datetime(
                        row.get("date", row.get("initiation_date", datetime.utcnow()))
                    ),
                    type=row.get("type", row.get("capa_type", "corrective")),
                    source=row.get("source", row.get("source_type", "Unknown")),
                    description=row.get("description", ""),
                    root_cause=row.get("root_cause", ""),
                    status=row.get("status", "open"),
                )
                db.add(capa)
            records_count += 1

    elif data_type == "equipment":
        for _, row in df.iterrows():
            eq_id = row.get("equipment_id", f"EQ-{records_count}")
            existing = (
                db.query(models.Equipment)
                .filter(models.Equipment.equipment_id == eq_id)
                .first()
            )
            if existing:
                existing.name = row.get("name", "Unknown")
                existing.calibration_date = pd.to_datetime(
                    row.get("calibration_date", datetime.utcnow())
                )
                existing.next_calibration = pd.to_datetime(
                    row.get("next_calibration", datetime.utcnow())
                )
                existing.status = row.get("status", "ok")
                existing.parameter = row.get("parameter", "")
                existing.deviation = float(row.get("deviation", 0))
            else:
                equipment = models.Equipment(
                    equipment_id=eq_id,
                    name=row.get("name", "Unknown"),
                    calibration_date=pd.to_datetime(
                        row.get("calibration_date", datetime.utcnow())
                    ),
                    next_calibration=pd.to_datetime(
                        row.get("next_calibration", datetime.utcnow())
                    ),
                    status=row.get("status", "ok"),
                    parameter=row.get("parameter", ""),
                    deviation=float(row.get("deviation", 0)),
                )
                db.add(equipment)
            records_count += 1

    upload_record = models.UploadedFile(
        filename=file.filename, data_type=data_type, records_count=records_count
    )
    db.add(upload_record)
    db.commit()

    return UploadResponse(
        filename=file.filename, records_imported=records_count, data_type=data_type
    )


@router.get("/uploads")
async def get_uploads(db: Session = Depends(get_db)):
    return (
        db.query(models.UploadedFile)
        .order_by(models.UploadedFile.uploaded_at.desc())
        .all()
    )
