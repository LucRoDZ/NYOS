from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.db import get_db
from app import models
from datetime import datetime, timedelta
from typing import Optional
import numpy as np
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get comprehensive analytics overview for dashboard"""

    # Date range
    max_date = db.query(func.max(models.Batch.manufacturing_date)).scalar()
    min_date = db.query(func.min(models.Batch.manufacturing_date)).scalar()

    if not max_date:
        return {
            "has_data": False,
            "message": "No data available. Please import data first.",
        }

    # Global stats
    total_batches = db.query(models.Batch).count()
    total_qc = db.query(models.QCResult).count()

    # Yield statistics
    avg_yield = db.query(func.avg(models.Batch.yield_percent)).scalar() or 0
    min_yield = db.query(func.min(models.Batch.yield_percent)).scalar() or 0
    max_yield = db.query(func.max(models.Batch.yield_percent)).scalar() or 0

    # Recent month stats
    month_ago = max_date - timedelta(days=30)
    recent_batches = (
        db.query(models.Batch)
        .filter(models.Batch.manufacturing_date >= month_ago)
        .count()
    )
    recent_yield = (
        db.query(func.avg(models.Batch.yield_percent))
        .filter(models.Batch.manufacturing_date >= month_ago)
        .scalar()
        or 0
    )

    # Quality metrics - use actual specs not overall_result field
    # Pharma specs: Assay 95-105%, Dissolution >80%
    qc_pass_count = (
        db.query(models.QCResult)
        .filter(
            models.QCResult.assay_percent >= 95,
            models.QCResult.assay_percent <= 105,
            models.QCResult.dissolution_mean >= 80,
        )
        .count()
    )
    qc_pass_rate = (qc_pass_count / total_qc * 100) if total_qc > 0 else 0

    # Complaints
    total_complaints = db.query(models.Complaint).count()
    open_complaints = (
        db.query(models.Complaint)
        .filter(func.lower(models.Complaint.status) == "open")
        .count()
    )

    # Complaints by severity
    critical_complaints = (
        db.query(models.Complaint)
        .filter(func.lower(models.Complaint.severity) == "critical")
        .count()
    )

    # CAPAs - count all non-closed as open
    total_capas = db.query(models.CAPA).count()
    open_capas = (
        db.query(models.CAPA)
        .filter(~func.lower(models.CAPA.status).like("%closed%"))
        .count()
    )
    overdue_capas = (
        db.query(models.CAPA)
        .filter(func.lower(models.CAPA.status) == "overdue")
        .count()
    )

    # Equipment
    total_calibrations = db.query(models.Equipment).count()
    failed_calibrations = (
        db.query(models.Equipment).filter(models.Equipment.result == "Fail").count()
    )

    # Calculate quality score (0-100)
    quality_score = calculate_quality_score(
        qc_pass_rate, avg_yield, open_complaints, open_capas, failed_calibrations
    )

    return {
        "has_data": True,
        "period": {
            "start": min_date.isoformat() if min_date else None,
            "end": max_date.isoformat() if max_date else None,
            "years": (
                (max_date.year - min_date.year + 1) if min_date and max_date else 0
            ),
        },
        "production": {
            "total_batches": total_batches,
            "recent_batches": recent_batches,
            "avg_yield": round(avg_yield, 2),
            "recent_yield": round(recent_yield, 2),
            "yield_range": {"min": round(min_yield, 2), "max": round(max_yield, 2)},
        },
        "quality": {
            "total_tests": total_qc,
            "pass_rate": round(qc_pass_rate, 2),
            "quality_score": quality_score,
        },
        "compliance": {
            "total_complaints": total_complaints,
            "open_complaints": open_complaints,
            "critical_complaints": critical_complaints,
            "total_capas": total_capas,
            "open_capas": open_capas,
            "overdue_capas": overdue_capas,
        },
        "equipment": {
            "total_calibrations": total_calibrations,
            "failed_calibrations": failed_calibrations,
            "calibration_pass_rate": round(
                (
                    (
                        (total_calibrations - failed_calibrations)
                        / total_calibrations
                        * 100
                    )
                    if total_calibrations > 0
                    else 100
                ),
                2,
            ),
        },
    }


def calculate_quality_score(
    qc_pass_rate, avg_yield, open_complaints, open_capas, failed_calibrations
):
    """Calculate overall quality score 0-100

    Weights optimized for pharmaceutical manufacturing:
    - QC pass rate: most important (40%)
    - Yield: important for efficiency (25%)
    - Complaints/CAPAs: normalized for long-term data (20%)
    - Equipment calibration: safety critical (15%)
    """
    score = 100

    # QC pass rate impact (max -40) - most critical
    if qc_pass_rate < 100:
        score -= (100 - qc_pass_rate) * 4  # 4 points per %

    # Yield impact (max -25)
    if avg_yield < 98:
        score -= (98 - avg_yield) * 5  # 5 points per % below 98

    # Open complaints impact (max -10) - scaled for realistic numbers
    # Typical pharma: <10 open complaints is good, >50 is concerning
    complaint_penalty = min(open_complaints / 5, 10)
    score -= complaint_penalty

    # Open CAPAs impact (max -10) - scaled for realistic numbers
    # Having some CAPAs open is normal; >100 is concerning
    capa_penalty = min(open_capas / 25, 10)
    score -= capa_penalty

    # Failed calibrations impact (max -15)
    score -= min(failed_calibrations, 15)

    return max(0, min(100, round(score, 1)))


@router.get("/drift-detection")
async def detect_drifts(db: Session = Depends(get_db), window_days: int = 90):
    """Detect drift trends in key parameters"""

    max_date = db.query(func.max(models.Batch.manufacturing_date)).scalar()
    if not max_date:
        return {"drifts": [], "message": "No data available"}

    window_start = max_date - timedelta(days=window_days)
    comparison_start = window_start - timedelta(days=window_days)

    drifts = []

    # Parameters to check for drift
    params = [
        ("hardness", models.Batch.hardness, "Hardness (kp)", 5),
        ("yield_percent", models.Batch.yield_percent, "Yield (%)", 2),
        (
            "compression_force",
            models.Batch.compression_force,
            "Compression Force (kN)",
            2,
        ),
        ("weight", models.Batch.weight, "Weight (mg)", 5),
    ]

    for param_id, column, label, threshold in params:
        # Current period stats
        current_avg = (
            db.query(func.avg(column))
            .filter(models.Batch.manufacturing_date >= window_start)
            .scalar()
        )

        # Previous period stats
        prev_avg = (
            db.query(func.avg(column))
            .filter(
                models.Batch.manufacturing_date >= comparison_start,
                models.Batch.manufacturing_date < window_start,
            )
            .scalar()
        )

        if current_avg and prev_avg:
            change = current_avg - prev_avg
            change_pct = (change / prev_avg) * 100 if prev_avg != 0 else 0

            # Check by equipment
            equipment_drifts = analyze_equipment_drift(
                db, column, window_start, comparison_start, threshold
            )

            if abs(change) > threshold or equipment_drifts:
                drifts.append(
                    {
                        "parameter": param_id,
                        "label": label,
                        "current_avg": round(current_avg, 2),
                        "previous_avg": round(prev_avg, 2),
                        "change": round(change, 2),
                        "change_pct": round(change_pct, 2),
                        "direction": "hausse" if change > 0 else "baisse",
                        "alert": abs(change) > threshold,
                        "equipment_drifts": equipment_drifts,
                    }
                )

    # Sort by absolute change percentage
    drifts.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

    return {
        "period": f"Last {window_days} days vs previous {window_days} days",
        "drifts": drifts,
        "total_alerts": len([d for d in drifts if d["alert"]]),
    }


def analyze_equipment_drift(db, column, current_start, prev_start, threshold):
    """Analyze drift by equipment"""
    equipment_drifts = []

    # Get unique presses
    presses = db.query(models.Batch.tablet_press_id).distinct().all()

    for (press,) in presses:
        if not press:
            continue

        current_avg = (
            db.query(func.avg(column))
            .filter(
                models.Batch.manufacturing_date >= current_start,
                models.Batch.tablet_press_id == press,
            )
            .scalar()
        )

        prev_avg = (
            db.query(func.avg(column))
            .filter(
                models.Batch.manufacturing_date >= prev_start,
                models.Batch.manufacturing_date < current_start,
                models.Batch.tablet_press_id == press,
            )
            .scalar()
        )

        if current_avg and prev_avg:
            change = current_avg - prev_avg
            if abs(change) > threshold * 1.5:  # Higher threshold for equipment-specific
                equipment_drifts.append(
                    {
                        "equipment": press,
                        "current_avg": round(current_avg, 2),
                        "previous_avg": round(prev_avg, 2),
                        "change": round(change, 2),
                    }
                )

    return equipment_drifts


@router.get("/supplier-performance")
async def get_supplier_performance(db: Session = Depends(get_db)):
    """Analyze supplier quality performance"""

    # Get raw materials with supplier info
    suppliers = (
        db.query(
            models.RawMaterial.supplier_id,
            models.RawMaterial.supplier_name,
            func.count(models.RawMaterial.id).label("deliveries"),
            func.sum(
                case((models.RawMaterial.disposition.like("Released%"), 1), else_=0)
            ).label("approved"),
            func.sum(
                case((models.RawMaterial.disposition == "Rejected", 1), else_=0)
            ).label("rejected"),
            func.sum(
                case((models.RawMaterial.disposition.like("Pending%"), 1), else_=0)
            ).label("pending"),
        )
        .group_by(models.RawMaterial.supplier_id, models.RawMaterial.supplier_name)
        .all()
    )

    result = []
    for s in suppliers:
        approval_rate = (s.approved / s.deliveries * 100) if s.deliveries > 0 else 0
        result.append(
            {
                "supplier_id": s.supplier_id,
                "supplier_name": s.supplier_name,
                "total_deliveries": s.deliveries,
                "approved": s.approved,
                "rejected": s.rejected,
                "pending": s.pending,
                "approval_rate": round(approval_rate, 2),
                "status": (
                    "good"
                    if approval_rate >= 98
                    else ("warning" if approval_rate >= 95 else "critical")
                ),
            }
        )

    # Sort by approval rate
    result.sort(key=lambda x: x["approval_rate"])

    return {
        "total_suppliers": len(result),
        "suppliers": result,
        "at_risk": len([s for s in result if s["status"] == "critical"]),
    }


@router.get("/period-comparison")
async def compare_periods(
    db: Session = Depends(get_db),
    period1_start: Optional[str] = None,
    period1_end: Optional[str] = None,
    period2_start: Optional[str] = None,
    period2_end: Optional[str] = None,
):
    """Compare two time periods"""

    max_date = db.query(func.max(models.Batch.manufacturing_date)).scalar()
    if not max_date:
        return {"error": "No data available"}

    # Default periods: current year vs previous year
    if not period1_start:
        period1_start = (max_date - timedelta(days=365)).strftime("%Y-%m-%d")
        period1_end = max_date.strftime("%Y-%m-%d")
        period2_start = (max_date - timedelta(days=730)).strftime("%Y-%m-%d")
        period2_end = (max_date - timedelta(days=365)).strftime("%Y-%m-%d")

    p1_start = datetime.strptime(period1_start, "%Y-%m-%d")
    p1_end = datetime.strptime(period1_end, "%Y-%m-%d")
    p2_start = datetime.strptime(period2_start, "%Y-%m-%d")
    p2_end = datetime.strptime(period2_end, "%Y-%m-%d")

    def get_period_stats(start, end):
        batches = (
            db.query(models.Batch)
            .filter(
                models.Batch.manufacturing_date >= start,
                models.Batch.manufacturing_date <= end,
            )
            .count()
        )

        avg_yield = (
            db.query(func.avg(models.Batch.yield_percent))
            .filter(
                models.Batch.manufacturing_date >= start,
                models.Batch.manufacturing_date <= end,
            )
            .scalar()
            or 0
        )

        avg_hardness = (
            db.query(func.avg(models.Batch.hardness))
            .filter(
                models.Batch.manufacturing_date >= start,
                models.Batch.manufacturing_date <= end,
            )
            .scalar()
            or 0
        )

        complaints = (
            db.query(models.Complaint)
            .filter(
                models.Complaint.complaint_date >= start,
                models.Complaint.complaint_date <= end,
            )
            .count()
        )

        return {
            "batches": batches,
            "avg_yield": round(avg_yield, 2),
            "avg_hardness": round(avg_hardness, 2),
            "complaints": complaints,
        }

    period1_stats = get_period_stats(p1_start, p1_end)
    period2_stats = get_period_stats(p2_start, p2_end)

    # Calculate changes
    def calc_change(curr, prev):
        if prev == 0:
            return 0
        return round((curr - prev) / prev * 100, 2)

    return {
        "period1": {
            "start": period1_start,
            "end": period1_end,
            "label": "Période actuelle",
            **period1_stats,
        },
        "period2": {
            "start": period2_start,
            "end": period2_end,
            "label": "Période précédente",
            **period2_stats,
        },
        "changes": {
            "batches_pct": calc_change(
                period1_stats["batches"], period2_stats["batches"]
            ),
            "yield_pct": calc_change(
                period1_stats["avg_yield"], period2_stats["avg_yield"]
            ),
            "hardness_pct": calc_change(
                period1_stats["avg_hardness"], period2_stats["avg_hardness"]
            ),
            "complaints_pct": calc_change(
                period1_stats["complaints"], period2_stats["complaints"]
            ),
        },
    }


@router.get("/anomalies")
async def detect_anomalies(db: Session = Depends(get_db), days: int = 30):
    """Detect anomalies in recent data"""

    max_date = db.query(func.max(models.Batch.manufacturing_date)).scalar()
    if not max_date:
        return {"anomalies": [], "message": "No data available"}

    cutoff = max_date - timedelta(days=days)
    anomalies = []

    # Check for low yield batches
    low_yield = (
        db.query(models.Batch)
        .filter(
            models.Batch.manufacturing_date >= cutoff, models.Batch.yield_percent < 95
        )
        .all()
    )

    for batch in low_yield:
        anomalies.append(
            {
                "type": "low_yield",
                "severity": "warning" if batch.yield_percent >= 90 else "critical",
                "batch_id": batch.batch_id,
                "date": (
                    batch.manufacturing_date.isoformat()
                    if batch.manufacturing_date
                    else None
                ),
                "value": batch.yield_percent,
                "message": f"Low yield: {batch.yield_percent}%",
                "equipment": batch.tablet_press_id,
            }
        )

    # Check for QC failures - only flag if values are actually out of spec
    # Pharma specs: Assay 95-105%, Dissolution >80%
    qc_issues = (
        db.query(models.QCResult)
        .filter(
            models.QCResult.test_date >= cutoff,
        )
        .all()
    )

    for qc in qc_issues:
        # Check actual values against pharmaceutical specifications
        issues = []
        is_critical = False

        # Assay check (95-105%)
        if qc.assay_percent and (qc.assay_percent < 95 or qc.assay_percent > 105):
            issues.append(f"Assay out of spec: {qc.assay_percent:.1f}%")
            is_critical = qc.assay_percent < 90 or qc.assay_percent > 110

        # Dissolution check (>80% at 30 min)
        if qc.dissolution_mean and qc.dissolution_mean < 80:
            issues.append(f"Low dissolution: {qc.dissolution_mean:.1f}%")
            is_critical = is_critical or qc.dissolution_mean < 70

        # Content uniformity check (AV < 15)
        # Note: Only check if value is realistic (some data may have % instead of AV)
        if qc.cu_av and qc.cu_av > 15 and qc.cu_av < 50:  # AV should be < 50
            issues.append(f"CU AV out of spec: {qc.cu_av:.1f}")
            is_critical = is_critical or qc.cu_av > 25

        # Total impurities check (<0.5%)
        if qc.impurity_total and qc.impurity_total > 0.5:
            issues.append(f"High impurities: {qc.impurity_total:.2f}%")
            is_critical = is_critical or qc.impurity_total > 1.0

        if issues:
            anomalies.append(
                {
                    "type": "qc_failure",
                    "severity": "critical" if is_critical else "warning",
                    "batch_id": qc.batch_id,
                    "date": qc.test_date.isoformat() if qc.test_date else None,
                    "message": f"Problème QC sur lot {qc.batch_id}",
                    "details": "; ".join(issues),
                }
            )

    # Check for equipment calibration failures
    cal_failures = (
        db.query(models.Equipment)
        .filter(
            models.Equipment.actual_date >= cutoff, models.Equipment.result == "Fail"
        )
        .all()
    )

    for eq in cal_failures:
        anomalies.append(
            {
                "type": "calibration_failure",
                "severity": "warning",
                "equipment_id": eq.equipment_id,
                "equipment_name": eq.equipment_name,
                "date": eq.actual_date.isoformat() if eq.actual_date else None,
                "message": f"Échec calibration: {eq.equipment_name}",
                "parameter": eq.parameter,
            }
        )

    # Sort by severity and date
    severity_order = {"critical": 0, "warning": 1}
    anomalies.sort(
        key=lambda x: (severity_order.get(x["severity"], 2), x.get("date", "") or "")
    )

    return {
        "period": f"Derniers {days} jours",
        "total": len(anomalies),
        "critical": len([a for a in anomalies if a["severity"] == "critical"]),
        "warning": len([a for a in anomalies if a["severity"] == "warning"]),
        "anomalies": anomalies[:50],  # Limit to 50
    }


@router.get("/yearly-summary")
async def get_yearly_summary(db: Session = Depends(get_db)):
    """Get yearly summary for trend analysis"""

    batches = (
        db.query(
            extract("year", models.Batch.manufacturing_date).label("year"),
            func.count(models.Batch.id).label("batch_count"),
            func.avg(models.Batch.yield_percent).label("avg_yield"),
            func.avg(models.Batch.hardness).label("avg_hardness"),
        )
        .group_by(extract("year", models.Batch.manufacturing_date))
        .order_by("year")
        .all()
    )

    complaints_by_year = (
        db.query(
            extract("year", models.Complaint.complaint_date).label("year"),
            func.count(models.Complaint.id).label("count"),
        )
        .group_by(extract("year", models.Complaint.complaint_date))
        .all()
    )

    complaints_dict = {int(c.year): c.count for c in complaints_by_year}

    return {
        "years": [
            {
                "year": int(b.year),
                "batches": b.batch_count,
                "avg_yield": round(b.avg_yield, 2) if b.avg_yield else 0,
                "avg_hardness": round(b.avg_hardness, 2) if b.avg_hardness else 0,
                "complaints": complaints_dict.get(int(b.year), 0),
            }
            for b in batches
            if b.year
        ]
    }


@router.get("/equipment-analysis")
async def get_equipment_analysis(db: Session = Depends(get_db)):
    """Analyze equipment performance"""

    # By tablet press - get basic stats (SQLite doesn't support stddev)
    presses = (
        db.query(
            models.Batch.tablet_press_id,
            func.count(models.Batch.id).label("batch_count"),
            func.avg(models.Batch.yield_percent).label("avg_yield"),
            func.avg(models.Batch.hardness).label("avg_hardness"),
        )
        .group_by(models.Batch.tablet_press_id)
        .all()
    )

    equipment_stats = []
    for p in presses:
        if not p.tablet_press_id:
            continue

        # Calculate standard deviation in Python
        hardness_values = (
            db.query(models.Batch.hardness)
            .filter(models.Batch.tablet_press_id == p.tablet_press_id)
            .filter(models.Batch.hardness.isnot(None))
            .all()
        )
        hardness_list = [h[0] for h in hardness_values if h[0] is not None]
        hardness_std = float(np.std(hardness_list)) if len(hardness_list) > 1 else 0.0

        equipment_stats.append(
            {
                "equipment_id": p.tablet_press_id,
                "type": "Tablet Press",
                "batches": p.batch_count,
                "avg_yield": round(p.avg_yield, 2) if p.avg_yield else 0,
                "avg_hardness": round(p.avg_hardness, 2) if p.avg_hardness else 0,
                "hardness_variability": round(hardness_std, 2),
            }
        )

    # Sort by yield
    equipment_stats.sort(key=lambda x: x["avg_yield"])

    return {
        "equipment": equipment_stats,
        "lowest_yield": equipment_stats[0] if equipment_stats else None,
        "highest_variability": (
            max(equipment_stats, key=lambda x: x["hardness_variability"])
            if equipment_stats
            else None
        ),
    }
