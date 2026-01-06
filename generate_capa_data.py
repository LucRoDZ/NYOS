"""
NYOS APR - Part 6: CAPA Records
================================
Corrective and Preventive Action tracking system.
Linked to deviations, complaints, audit findings, and OOS investigations.
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
OUTPUT_DIR = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "apr_data") + os.sep
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CAPA_SOURCES = {
    "Deviation": 0.35,
    "Customer Complaint": 0.20,
    "OOS Investigation": 0.15,
    "Internal Audit": 0.10,
    "External Audit": 0.05,
    "Management Review": 0.05,
    "Trend Analysis": 0.05,
    "Self-Identified": 0.05,
}

ROOT_CAUSE_CATEGORIES = [
    "Procedure not followed",
    "Procedure inadequate",
    "Training deficiency",
    "Equipment malfunction",
    "Environmental factor",
    "Raw material variation",
    "Human error",
    "Communication failure",
    "Design flaw",
    "Supplier issue",
]

DEPARTMENTS = [
    "Manufacturing",
    "Quality Control",
    "Quality Assurance",
    "Warehouse",
    "Engineering",
    "Packaging",
]

EFFECTIVENESS_CHECK_METHODS = [
    "Re-audit",
    "Trend monitoring",
    "Process capability study",
    "Deviation tracking",
    "KPI review",
]


def generate_capa_data(year: int):
    """
    Generate CAPA records with:
    - Source linkage (deviation, complaint, audit, etc.)
    - Root cause analysis details
    - Action items and timelines
    - Effectiveness verification
    """
    print(f"\n🔧 Generating CAPA Data for {year}...")

    # Base number of CAPAs per year
    num_capas = random.randint(80, 120)

    # More CAPAs in problematic years
    if year == 2022:
        num_capas = int(num_capas * 1.2)  # Excipient supplier issue
    if year == 2025:
        num_capas = int(num_capas * 1.15)  # API supplier change

    records = []

    for i in range(num_capas):
        capa_open_date = datetime(year, random.randint(1, 12), random.randint(1, 28))

        # Source determination
        source = np.random.choice(
            list(CAPA_SOURCES.keys()), p=list(CAPA_SOURCES.values())
        )

        # Source reference
        if source == "Deviation":
            source_ref = f"DEV-{year}-{random.randint(1, 500):04d}"
        elif source == "Customer Complaint":
            source_ref = f"COMP-{year}-{random.randint(1, 100):05d}"
        elif source == "OOS Investigation":
            source_ref = f"OOS-{year}-{random.randint(1, 50):04d}"
        elif source == "Internal Audit":
            source_ref = f"IA-{year}-{random.randint(1, 20):03d}"
        elif source == "External Audit":
            source_ref = f"EA-{year}-{random.randint(1, 5):03d}"
        else:
            source_ref = f"MR-{year}-{random.randint(1, 12):02d}"

        # CAPA type
        capa_type = random.choice(
            ["Corrective", "Preventive", "Corrective & Preventive"]
        )

        # Problem classification
        problem_category = random.choice(
            [
                "Documentation",
                "Equipment",
                "Process",
                "Training",
                "Material",
                "Environmental Control",
                "System/Software",
                "Supplier/Vendor",
            ]
        )

        # Risk assessment
        probability = random.choice(["High", "Medium", "Low"])
        severity = random.choice(["Critical", "Major", "Minor"])
        risk_score = {
            ("High", "Critical"): "Critical",
            ("High", "Major"): "High",
            ("High", "Minor"): "Medium",
            ("Medium", "Critical"): "High",
            ("Medium", "Major"): "Medium",
            ("Medium", "Minor"): "Low",
            ("Low", "Critical"): "Medium",
            ("Low", "Major"): "Low",
            ("Low", "Minor"): "Low",
        }[(probability, severity)]

        # Root cause analysis
        rca_method = random.choice(
            [
                "5-Why",
                "Fishbone Diagram",
                "Fault Tree Analysis",
                "FMEA",
                "Is/Is-Not Analysis",
            ]
        )
        root_cause = random.choice(ROOT_CAUSE_CATEGORIES)

        # Department assignment
        responsible_dept = random.choice(DEPARTMENTS)
        owner = f"{responsible_dept[:3].upper()}-{random.randint(1, 30):02d}"

        # Action planning
        num_actions = random.randint(1, 5)
        action_descriptions = []
        for j in range(num_actions):
            action_type = random.choice(
                [
                    "Update SOP",
                    "Retrain personnel",
                    "Implement process control",
                    "Install equipment monitoring",
                    "Qualify new supplier",
                    "Revise specification",
                    "Add IPC checkpoint",
                    "Implement automation",
                ]
            )
            action_descriptions.append(action_type)

        # Timeline
        target_days = {"Critical": 30, "High": 60, "Medium": 90, "Low": 120}[risk_score]

        target_date = capa_open_date + timedelta(days=target_days)

        # Completion status
        days_since_open = (datetime(year, 12, 31) - capa_open_date).days

        if days_since_open > target_days + 30:
            status = random.choices(
                ["Closed - Effective", "Closed - Not Effective", "Overdue"],
                weights=[0.7, 0.1, 0.2],
            )[0]
        elif days_since_open > target_days:
            status = random.choices(
                ["Closed - Effective", "In Progress", "Overdue"],
                weights=[0.5, 0.3, 0.2],
            )[0]
        elif days_since_open > target_days * 0.5:
            status = random.choices(
                ["Closed - Effective", "In Progress", "On Hold"],
                weights=[0.3, 0.6, 0.1],
            )[0]
        else:
            status = random.choices(
                ["In Progress", "Investigation", "Planning"], weights=[0.4, 0.3, 0.3]
            )[0]

        # Completion dates based on status
        if "Closed" in status:
            actual_completion = capa_open_date + timedelta(
                days=random.randint(target_days - 15, target_days + 30)
            )
            days_late = max(0, (actual_completion - target_date).days)
        else:
            actual_completion = None
            days_late = None

        # Effectiveness verification
        if status == "Closed - Effective":
            effectiveness_verified = "Yes"
            effectiveness_date = actual_completion + timedelta(
                days=random.randint(30, 90)
            )
            effectiveness_method = random.choice(EFFECTIVENESS_CHECK_METHODS)
            recurrence = "No"
        elif status == "Closed - Not Effective":
            effectiveness_verified = "Yes"
            effectiveness_date = actual_completion + timedelta(
                days=random.randint(30, 90)
            )
            effectiveness_method = random.choice(EFFECTIVENESS_CHECK_METHODS)
            recurrence = "Yes"
        else:
            effectiveness_verified = "Pending"
            effectiveness_date = None
            effectiveness_method = random.choice(EFFECTIVENESS_CHECK_METHODS)
            recurrence = "N/A"

        # Extensions
        num_extensions = random.choices([0, 1, 2], weights=[0.7, 0.25, 0.05])[0]
        if num_extensions > 0:
            extension_reason = random.choice(
                [
                    "Resource constraint",
                    "Additional investigation required",
                    "Pending supplier response",
                    "Equipment lead time",
                    "Regulatory guidance awaited",
                ]
            )
        else:
            extension_reason = ""

        records.append(
            {
                "capa_id": f"CAPA-{year}-{i+1:04d}",
                "capa_type": capa_type,
                "source": source,
                "source_reference": source_ref,
                "open_date": capa_open_date.strftime("%Y-%m-%d"),
                "problem_statement": f"Issue identified through {source.lower()} requiring {capa_type.lower()} action",
                "problem_category": problem_category,
                "product_affected": (
                    "PARA-500-TAB" if random.random() > 0.2 else "Multiple Products"
                ),
                "batch_affected": (
                    f"PARA-{str(year)[-2:]}-{random.randint(1, 7000):04d}"
                    if source in ["Deviation", "OOS Investigation"]
                    else "N/A"
                ),
                "risk_probability": probability,
                "risk_severity": severity,
                "risk_score": risk_score,
                "rca_method": rca_method,
                "root_cause_category": root_cause,
                "root_cause_description": f"Root cause determined using {rca_method}: {root_cause}",
                "contributing_factors": random.choice(
                    [
                        "Workload",
                        "Shift change",
                        "New personnel",
                        "Equipment age",
                        "None identified",
                    ]
                ),
                "responsible_department": responsible_dept,
                "capa_owner": owner,
                "approver": f"QA-MGR-{random.randint(1, 5):02d}",
                "num_actions": num_actions,
                "action_summary": "; ".join(action_descriptions),
                "target_date": target_date.strftime("%Y-%m-%d"),
                "actual_completion_date": (
                    actual_completion.strftime("%Y-%m-%d") if actual_completion else ""
                ),
                "days_to_close": (
                    (actual_completion - capa_open_date).days
                    if actual_completion
                    else None
                ),
                "days_late": days_late,
                "status": status,
                "num_extensions": num_extensions,
                "extension_reason": extension_reason,
                "effectiveness_check_method": effectiveness_method,
                "effectiveness_verified": effectiveness_verified,
                "effectiveness_date": (
                    effectiveness_date.strftime("%Y-%m-%d")
                    if effectiveness_date
                    else ""
                ),
                "recurrence": recurrence,
                "linked_capas": (
                    f"CAPA-{year}-{random.randint(1, i+1):04d}"
                    if random.random() < 0.1 and i > 0
                    else ""
                ),
                "regulatory_impact": "Yes" if risk_score == "Critical" else "No",
                "cost_estimate_usd": (
                    random.randint(500, 50000) if status != "Planning" else None
                ),
                "created_by": f"QA-{random.randint(1, 15):02d}",
                "last_updated": (
                    capa_open_date + timedelta(days=random.randint(1, 30))
                ).strftime("%Y-%m-%d"),
                "comments": "",
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}capa_records_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} CAPA records")
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 6")
    print("CAPA (Corrective and Preventive Action) Records")
    print("=" * 70)

    all_capa = []
    for year in YEARS:
        df = generate_capa_data(year)
        if df is not None:
            all_capa.append(df)

    if all_capa:
        combined = pd.concat(all_capa, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}capa_records_ALL.csv", index=False)
        print(f"\n✅ Combined file: capa_records_ALL.csv ({len(combined):,} records)")
