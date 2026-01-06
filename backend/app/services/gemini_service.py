import google.generativeai as genai
from app.config import GOOGLE_API_KEY
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from datetime import datetime, timedelta
import json

genai.configure(api_key=GOOGLE_API_KEY)


def get_data_context(db: Session) -> str:
    """Build comprehensive context from all data sources"""
    batches = (
        db.query(models.Batch)
        .order_by(models.Batch.manufacturing_date.desc())
        .limit(50)
        .all()
    )
    qc_results = (
        db.query(models.QCResult)
        .order_by(models.QCResult.test_date.desc())
        .limit(50)
        .all()
    )
    complaints = db.query(models.Complaint).all()
    capas = db.query(models.CAPA).all()
    equipment = db.query(models.Equipment).limit(50).all()

    # Calculate statistics
    total_batches = db.query(models.Batch).count()
    avg_yield = db.query(func.avg(models.Batch.yield_percent)).scalar() or 0
    avg_hardness = db.query(func.avg(models.Batch.hardness)).scalar() or 0

    context = f"""
=== PHARMACEUTICAL PLANT DATA - PARACETAMOL 500mg ===
Analysis Period: 2020-2025 (6 years of APR data)

GLOBAL STATISTICS:
- Total batches produced: {total_batches:,}
- Average yield: {avg_yield:.1f}%
- Average hardness: {avg_hardness:.1f} kp
- Customer complaints: {len(complaints)} ({len([c for c in complaints if c.status == 'open'])} open)
- CAPAs: {len(capas)} ({len([c for c in capas if c.status == 'open'])} open)

RECENT BATCHES (last {len(batches)}):
"""
    for b in batches[:15]:
        date_str = (
            b.manufacturing_date.strftime("%Y-%m-%d") if b.manufacturing_date else "N/A"
        )
        context += f"- {b.batch_id}: {date_str}, Press: {b.tablet_press_id or 'N/A'}, Hardness: {b.hardness or 0:.1f}kp, Yield: {b.yield_percent or 0:.1f}%\n"

    if qc_results:
        context += f"\nRECENT QC RESULTS ({len(qc_results)} tests):\n"
        for qc in qc_results[:15]:
            context += f"- {qc.batch_id}: Assay={qc.assay_percent or 0:.1f}%, Dissolution={qc.dissolution_mean or 0:.1f}%, Result: {qc.overall_result}\n"

    if complaints:
        context += f"\nCUSTOMER COMPLAINTS ({len(complaints)} total):\n"
        open_complaints = [
            c for c in complaints if c.status and c.status.lower() == "open"
        ]
        context += f"   Open: {len(open_complaints)}\n"
        by_category = {}
        for c in complaints:
            cat = c.category or "Other"
            by_category[cat] = by_category.get(cat, 0) + 1
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1])[:5]:
            context += f"   - {cat}: {count}\n"
        by_severity = {}
        for c in complaints:
            sev = c.severity or "Unknown"
            by_severity[sev] = by_severity.get(sev, 0) + 1
        context += f"   By severity: {by_severity}\n"

    if capas:
        context += f"\nCAPAS ({len(capas)} total):\n"
        open_capas = [c for c in capas if c.status and "closed" not in c.status.lower()]
        context += f"   Open: {len(open_capas)}\n"
        by_source = {}
        for c in capas:
            src = c.source or "Other"
            by_source[src] = by_source.get(src, 0) + 1
        for src, count in sorted(by_source.items(), key=lambda x: -x[1])[:5]:
            context += f"   - Source {src}: {count}\n"
        critical = [c for c in capas if c.risk_score == "Critical"]
        context += f"   Critical CAPAs: {len(critical)}\n"

    if equipment:
        context += f"\nEQUIPMENT (recent calibrations):\n"
        failures = [e for e in equipment if e.result == "Fail"]
        context += f"   Calibration failures: {len(failures)}\n"
        by_type = {}
        for e in equipment:
            t = e.equipment_type or "Other"
            by_type[t] = by_type.get(t, 0) + 1
        context += f"   By type: {by_type}\n"

    return context


SYSTEM_PROMPT = """You are NYOS, an AI assistant expert in pharmaceutical quality and APR (Annual Product Review) analysis.
You analyze production data for Paracetamol 500mg tablets over a 6-year period (2020-2025).

Your role:
1. Detect trends and drifts in production data
2. Identify anomalies, weak signals, and potential issues
3. Analyze correlations between equipment, batches, and quality results
4. Clearly summarize the plant's quality situation
5. Recommend corrective and preventive actions

Hidden scenarios to detect:
- 2020: COVID-19 impact on production
- 2021: Press-A degradation (Sept-Nov)
- 2022: Excipient supplier issue MCC (June)
- 2023: Analytical method transition (Q2)
- 2024: Seasonal temperature effect (Jul-Aug)
- 2025: Press-B drift + New API supplier (Nov)

Rules:
- Be precise with numerical data
- Flag any potential issues
- Respond in English
- Use bullet points and markdown formatting
- Cite specific batches, dates, and values when relevant
"""


async def chat_with_gemini(message: str, db: Session) -> str:
    try:
        context = get_data_context(db)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        full_prompt = f"""{SYSTEM_PROMPT}

DATA CONTEXT:
{context}

USER QUESTION:
{message}

RESPONSE:"""

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Gemini connection error: {str(e)}. Check your API key."


async def analyze_trends(db: Session, parameter: str = "hardness", days: int = 30):
    batches = db.query(models.Batch).order_by(models.Batch.manufacturing_date).all()

    if not batches:
        return {"error": "Not enough data", "dates": [], "values": []}

    max_date = max(b.manufacturing_date for b in batches if b.manufacturing_date)
    cutoff = max_date - timedelta(days=days)

    filtered = [
        b for b in batches if b.manufacturing_date and b.manufacturing_date >= cutoff
    ]

    if len(filtered) < 2:
        return {
            "error": "Not enough data for this period",
            "dates": [],
            "values": [],
        }

    values = [
        getattr(b, parameter, 0)
        for b in filtered
        if getattr(b, parameter, None) is not None
    ]
    dates = [
        b.manufacturing_date.strftime("%Y-%m-%d")
        for b in filtered
        if getattr(b, parameter, None) is not None
    ]

    if len(values) < 2:
        return {"error": "Not enough data", "dates": [], "values": []}

    trend = "stable"
    alert = False
    if len(values) >= 5:
        mid = len(values) // 2
        first_avg = sum(values[:mid]) / mid
        last_avg = sum(values[mid:]) / (len(values) - mid)
        change = ((last_avg - first_avg) / first_avg) * 100 if first_avg else 0

        if change > 5:
            trend = "up"
            alert = True
        elif change < -5:
            trend = "down"
            alert = True

    return {
        "dates": dates,
        "values": values,
        "parameter": parameter,
        "trend_direction": trend,
        "alert": alert,
        "average": round(sum(values) / len(values), 2) if values else 0,
        "min": round(min(values), 2) if values else 0,
        "max": round(max(values), 2) if values else 0,
        "count": len(values),
    }


def get_full_stats(db: Session) -> dict:
    from sqlalchemy import func

    batches = db.query(models.Batch).all()
    qc_results = db.query(models.QCResult).all()
    complaints = db.query(models.Complaint).all()
    capas = db.query(models.CAPA).all()
    equipment = db.query(models.Equipment).all()

    # Calculate QC pass rate based on actual pharmaceutical specifications
    # Specs: Assay 95-105%, Dissolution >80%
    qc_pass_count = len(
        [
            q
            for q in qc_results
            if q.assay_percent
            and q.dissolution_mean
            and 95 <= q.assay_percent <= 105
            and q.dissolution_mean >= 80
        ]
    )

    stats = {
        "total_batches": len(batches),
        "avg_hardness": (
            round(
                sum(b.hardness for b in batches if b.hardness)
                / max(len([b for b in batches if b.hardness]), 1),
                2,
            )
            if batches
            else 0
        ),
        "avg_yield": (
            round(
                sum(b.yield_percent for b in batches if b.yield_percent)
                / max(len([b for b in batches if b.yield_percent]), 1),
                2,
            )
            if batches
            else 0
        ),
        "machines": {},
        "qc_pass_rate": (
            round(qc_pass_count / max(len(qc_results), 1) * 100, 1) if qc_results else 0
        ),
        "complaints_by_category": {},
        "complaints_open": len(
            [c for c in complaints if c.status and c.status.lower() == "open"]
        ),
        "capas_open": len(
            [c for c in capas if c.status and "closed" not in c.status.lower()]
        ),
        "equipment_due": len([e for e in equipment if e.result == "Fail"]),
    }

    for b in batches:
        machine = b.tablet_press_id or "Unknown"
        if machine not in stats["machines"]:
            stats["machines"][machine] = {
                "count": 0,
                "hardness_sum": 0,
                "yield_sum": 0,
            }
        stats["machines"][machine]["count"] += 1
        stats["machines"][machine]["hardness_sum"] += b.hardness or 0
        stats["machines"][machine]["yield_sum"] += b.yield_percent or 0

    for m, data in stats["machines"].items():
        if data["count"] > 0:
            data["avg_hardness"] = round(data["hardness_sum"] / data["count"], 2)
            data["avg_yield"] = round(data["yield_sum"] / data["count"], 2)

    for c in complaints:
        cat = c.category or "Unknown"
        stats["complaints_by_category"][cat] = (
            stats["complaints_by_category"].get(cat, 0) + 1
        )

    return stats


async def generate_summary_stream(db: Session):
    try:
        context = get_data_context(db)
        stats = get_full_stats(db)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        prompt = f"""{SYSTEM_PROMPT}

DATA CONTEXT:
{context}

STATISTICS:
- Total batches: {stats['total_batches']}
- Average hardness: {stats['avg_hardness']}N
- Average yield: {stats['avg_yield']}%
- QC compliance rate: {stats['qc_pass_rate']}%
- Open complaints: {stats['complaints_open']}
- Open CAPAs: {stats['capas_open']}
- Equipment requiring calibration: {stats['equipment_due']}
- Complaints by category: {stats['complaints_by_category']}
- Performance by machine: {stats['machines']}

Generate a detailed executive summary of the plant status.
Structure your response with:
1. **Overall Status** - (Good / Warning / Critical)
2. **Production Performance** - yield, volumes
3. **Quality** - QC results, trends
4. **Issues Detected** - complaints, CAPAs, anomalies
5. **Recommendations** - priority actions

Use bullet points and **bold** text for important points.

SUMMARY:"""

        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield f"data: {json.dumps({'text': chunk.text})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


async def generate_report(db: Session) -> str:
    try:
        context = get_data_context(db)
        stats = get_full_stats(db)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""You are a pharmaceutical quality expert. Generate a complete and professional APR (Annual Product Review) report.

PLANT DATA:
{context}

STATISTICS:
- Total batches produced: {stats['total_batches']}
- Average hardness: {stats['avg_hardness']}N
- Average yield: {stats['avg_yield']}%
- QC compliance rate: {stats['qc_pass_rate']}%
- Open complaints: {stats['complaints_open']}
- Open CAPAs: {stats['capas_open']}
- Equipment requiring calibration: {stats['equipment_due']}
- Complaints by category: {stats['complaints_by_category']}
- Performance by machine: {stats['machines']}

Generate a complete report with these sections:

# ANNUAL PRODUCT REVIEW REPORT (APR)
## Paracetamol 500mg - Year 2024

### 1. EXECUTIVE SUMMARY
(Overall status, key conclusions)

### 2. PRODUCTION PERFORMANCE
- Volumes produced
- Yields by period and machine
- Trend analysis

### 3. QUALITY CONTROL
- Test results (dissolution, assay, hardness, friability)
- Compliance rate
- Non-conformities detected

### 4. COMPLAINTS AND CLAIMS
- Analysis by category
- Trends
- Corrective actions

### 5. CORRECTIVE AND PREVENTIVE ACTIONS (CAPA)
- CAPAs initiated
- Closure status
- Effectiveness

### 6. EQUIPMENT
- Calibration status
- Preventive maintenance

### 7. TREND ANALYSIS
- Identified drifts
- Weak signals
- Comparison with previous period

### 8. CONCLUSIONS AND RECOMMENDATIONS
- Decision to maintain/modify process
- Priority actions for the following year

Be precise, use numerical data, and format properly in Markdown."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {str(e)}"
