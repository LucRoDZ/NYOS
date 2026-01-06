"""
NYOS APR - Part 9: Batch Release & Disposition
================================================
QP release decisions, batch review checklist, disposition tracking.
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

QUALIFIED_PERSONS = ["QP-001", "QP-002", "QP-003", "QP-004", "QP-005"]
QP_NAMES = {
    "QP-001": "Dr. Sarah Johnson",
    "QP-002": "Dr. Michael Chen",
    "QP-003": "Dr. Emily Williams",
    "QP-004": "Dr. David Brown",
    "QP-005": "Dr. Lisa Martinez",
}

RELEASE_CHECKLISTS = [
    "Batch record review complete",
    "All IPC results within specification",
    "QC testing complete and approved",
    "Deviation review complete",
    "Change control review complete",
    "Environmental monitoring acceptable",
    "Equipment calibration verified",
    "Raw material documentation verified",
    "Stability protocol assigned",
    "Label reconciliation complete",
    "Yield within acceptable limits",
    "Packaging integrity verified",
]


def generate_batch_release_data(year: int):
    """Generate batch release and disposition records."""
    print(f"\n📋 Generating Batch Release Data for {year}...")

    # Load manufacturing data to get batch info
    mfg_file = f"{OUTPUT_DIR}manufacturing_extended_{year}.csv"
    if not os.path.exists(mfg_file):
        print(f"   ⚠️  Manufacturing file not found")
        return None

    mfg_df = pd.read_csv(mfg_file)

    # Load QC data for test results
    qc_file = f"{OUTPUT_DIR}qc_extended_{year}.csv"
    qc_df = pd.read_csv(qc_file) if os.path.exists(qc_file) else None

    records = []

    for _, batch in mfg_df.iterrows():
        batch_id = batch["batch_id"]
        mfg_date = datetime.strptime(batch["manufacturing_date"], "%Y-%m-%d")

        # Batch review initiation
        review_start = mfg_date + timedelta(days=random.randint(1, 3))

        # QC testing duration
        qc_complete_date = review_start + timedelta(days=random.randint(5, 14))

        # Batch review duration
        batch_review_complete = qc_complete_date + timedelta(days=random.randint(1, 3))

        # QP review and release
        qp_review_date = batch_review_complete + timedelta(days=random.randint(1, 2))

        # Determine disposition based on various factors
        yield_value = batch.get("actual_yield_pct", 98.0)

        # Check for deviations (simulated)
        has_deviation = random.random() < 0.08
        deviation_critical = random.random() < 0.1 if has_deviation else False

        # Check for OOS (simulated from QC data)
        has_oos = random.random() < 0.03

        # Determine hold reasons
        hold_reasons = []
        if has_deviation:
            hold_reasons.append("Deviation pending closure")
        if has_oos:
            hold_reasons.append("OOS investigation pending")
        if yield_value < 95:
            hold_reasons.append("Low yield investigation")

        # Disposition decision
        if deviation_critical or (has_oos and random.random() > 0.7):
            disposition = "Rejected"
            release_date = None
            days_to_release = None
        elif hold_reasons:
            if random.random() > 0.3:
                disposition = "Released"
                release_date = qp_review_date + timedelta(days=random.randint(1, 14))
                days_to_release = (release_date - mfg_date).days
            else:
                disposition = "On Hold"
                release_date = None
                days_to_release = None
        else:
            disposition = "Released"
            release_date = qp_review_date
            days_to_release = (release_date - mfg_date).days

        # Assigned QP
        qp_id = random.choice(QUALIFIED_PERSONS)

        # Checklist completion
        checklist_items = {}
        for item in RELEASE_CHECKLISTS:
            if disposition == "Released":
                checklist_items[item] = "Yes"
            elif disposition == "On Hold":
                if "Deviation" in item or "OOS" in str(hold_reasons):
                    checklist_items[item] = "Pending"
                else:
                    checklist_items[item] = "Yes"
            else:
                checklist_items[item] = random.choice(["Yes", "No", "N/A"])

        # Expiry date calculation (3 years from manufacture)
        expiry_date = mfg_date + timedelta(days=365 * 3)

        # Market destination
        markets = ["Domestic", "Export - EU", "Export - US", "Export - RoW"]
        market_weights = [0.5, 0.2, 0.2, 0.1]
        market_destination = random.choices(markets, weights=market_weights)[0]

        # Regulatory submission status
        if market_destination in ["Export - EU", "Export - US"]:
            regulatory_clearance = "Required"
            clearance_status = "Approved" if disposition == "Released" else "Pending"
        else:
            regulatory_clearance = "Not Required"
            clearance_status = "N/A"

        records.append(
            {
                "batch_id": batch_id,
                "product_code": "PARA-500-TAB",
                "product_name": "Paracetamol 500mg Tablets",
                "batch_size_kg": batch.get("batch_size_kg", 200),
                "manufacturing_date": mfg_date.strftime("%Y-%m-%d"),
                "packaging_complete_date": (
                    mfg_date + timedelta(days=random.randint(1, 3))
                ).strftime("%Y-%m-%d"),
                "batch_review_start": review_start.strftime("%Y-%m-%d"),
                "qc_testing_complete": qc_complete_date.strftime("%Y-%m-%d"),
                "batch_review_complete": batch_review_complete.strftime("%Y-%m-%d"),
                "qp_id": qp_id,
                "qp_name": QP_NAMES[qp_id],
                "qp_review_date": qp_review_date.strftime("%Y-%m-%d"),
                "actual_yield_pct": yield_value,
                "theoretical_tablets": int(
                    batch.get("batch_size_kg", 200) * 1000 / 0.6
                ),
                "actual_tablets": int(
                    batch.get("batch_size_kg", 200) * 1000 / 0.6 * yield_value / 100
                ),
                "has_deviation": "Yes" if has_deviation else "No",
                "deviation_reference": (
                    f"DEV-{year}-{random.randint(1, 500):04d}" if has_deviation else ""
                ),
                "deviation_classification": (
                    random.choice(["Major", "Minor"]) if has_deviation else ""
                ),
                "deviation_closed": (
                    "Yes"
                    if has_deviation and disposition == "Released"
                    else ("No" if has_deviation else "")
                ),
                "has_oos": "Yes" if has_oos else "No",
                "oos_reference": (
                    f"OOS-{year}-{random.randint(1, 100):04d}" if has_oos else ""
                ),
                "oos_resolved": (
                    "Yes"
                    if has_oos and disposition == "Released"
                    else ("No" if has_oos else "")
                ),
                "change_control_applicable": "Yes" if random.random() < 0.1 else "No",
                "change_control_reference": (
                    f"CC-{year}-{random.randint(1, 50):03d}"
                    if random.random() < 0.1
                    else ""
                ),
                "checklist_batch_record": checklist_items.get(
                    "Batch record review complete", "Yes"
                ),
                "checklist_ipc": checklist_items.get(
                    "All IPC results within specification", "Yes"
                ),
                "checklist_qc_complete": checklist_items.get(
                    "QC testing complete and approved", "Yes"
                ),
                "checklist_deviation": checklist_items.get(
                    "Deviation review complete", "Yes"
                ),
                "checklist_change_control": checklist_items.get(
                    "Change control review complete", "Yes"
                ),
                "checklist_environmental": checklist_items.get(
                    "Environmental monitoring acceptable", "Yes"
                ),
                "checklist_calibration": checklist_items.get(
                    "Equipment calibration verified", "Yes"
                ),
                "checklist_raw_materials": checklist_items.get(
                    "Raw material documentation verified", "Yes"
                ),
                "checklist_stability": checklist_items.get(
                    "Stability protocol assigned", "Yes"
                ),
                "checklist_label": checklist_items.get(
                    "Label reconciliation complete", "Yes"
                ),
                "checklist_yield": checklist_items.get(
                    "Yield within acceptable limits", "Yes"
                ),
                "checklist_packaging": checklist_items.get(
                    "Packaging integrity verified", "Yes"
                ),
                "disposition": disposition,
                "disposition_date": (
                    release_date.strftime("%Y-%m-%d") if release_date else ""
                ),
                "hold_reason": "; ".join(hold_reasons) if hold_reasons else "",
                "rejection_reason": (
                    "Quality failure" if disposition == "Rejected" else ""
                ),
                "days_to_release": days_to_release,
                "expedited_release": (
                    "Yes" if days_to_release and days_to_release < 10 else "No"
                ),
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "shelf_life_months": 36,
                "retest_date": (mfg_date + timedelta(days=365 * 2)).strftime(
                    "%Y-%m-%d"
                ),
                "market_destination": market_destination,
                "regulatory_clearance": regulatory_clearance,
                "clearance_status": clearance_status,
                "stability_protocol": f"STAB-{year}-{random.randint(1, 50):03d}",
                "stability_station": random.choice(
                    ["Long-term", "Accelerated", "Both"]
                ),
                "warehouse_location": f"FG-{random.choice(['A', 'B', 'C'])}-{random.randint(1, 100):03d}",
                "shipped_quantity_pct": (
                    random.randint(0, 100) if disposition == "Released" else 0
                ),
                "comments": "",
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}batch_release_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} batch release records")

    # Summary statistics
    released = len(df[df["disposition"] == "Released"])
    on_hold = len(df[df["disposition"] == "On Hold"])
    rejected = len(df[df["disposition"] == "Rejected"])
    print(f"      Released: {released} | On Hold: {on_hold} | Rejected: {rejected}")

    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 9")
    print("Batch Release & Disposition")
    print("=" * 70)

    all_release = []

    for year in YEARS:
        df = generate_batch_release_data(year)
        if df is not None:
            all_release.append(df)

    if all_release:
        combined = pd.concat(all_release, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}batch_release_ALL.csv", index=False)
        print(f"\n✅ Combined file: batch_release_ALL.csv ({len(combined):,} records)")

        # Overall summary
        print("\n📊 Overall Summary:")
        print(f"   Total batches: {len(combined):,}")
        print(f"   Released: {len(combined[combined['disposition'] == 'Released']):,}")
        print(f"   On Hold: {len(combined[combined['disposition'] == 'On Hold']):,}")
        print(f"   Rejected: {len(combined[combined['disposition'] == 'Rejected']):,}")
