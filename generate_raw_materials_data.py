"""
NYOS APR - Part 7: Raw Material & Supplier Data
=================================================
Material receipts, COA verification, incoming inspection,
supplier qualification and performance tracking.
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

# Material master data
MATERIALS = {
    "RM-API-001": {
        "name": "Paracetamol API",
        "category": "Active Pharmaceutical Ingredient",
        "unit": "kg",
        "spec": "USP/EP Monograph",
        "storage": "Controlled Room Temperature (15-25°C)",
        "retest_months": 24,
    },
    "RM-EXC-001": {
        "name": "Microcrystalline Cellulose (MCC) PH-102",
        "category": "Excipient - Diluent/Binder",
        "unit": "kg",
        "spec": "USP-NF/EP",
        "storage": "Room Temperature",
        "retest_months": 36,
    },
    "RM-EXC-002": {
        "name": "Povidone K30 (PVP K30)",
        "category": "Excipient - Binder",
        "unit": "kg",
        "spec": "USP-NF/EP",
        "storage": "Controlled Room Temperature",
        "retest_months": 24,
    },
    "RM-EXC-003": {
        "name": "Croscarmellose Sodium",
        "category": "Excipient - Disintegrant",
        "unit": "kg",
        "spec": "USP-NF/EP",
        "storage": "Room Temperature",
        "retest_months": 36,
    },
    "RM-EXC-004": {
        "name": "Magnesium Stearate",
        "category": "Excipient - Lubricant",
        "unit": "kg",
        "spec": "USP-NF/EP",
        "storage": "Room Temperature",
        "retest_months": 36,
    },
    "RM-EXC-005": {
        "name": "Colloidal Silicon Dioxide",
        "category": "Excipient - Glidant",
        "unit": "kg",
        "spec": "USP-NF/EP",
        "storage": "Room Temperature",
        "retest_months": 36,
    },
    "PM-PRI-001": {
        "name": "HDPE Bottle 100cc",
        "category": "Primary Packaging",
        "unit": "pcs",
        "spec": "In-house Spec",
        "storage": "Room Temperature",
        "retest_months": 60,
    },
    "PM-SEC-001": {
        "name": "Carton Box",
        "category": "Secondary Packaging",
        "unit": "pcs",
        "spec": "In-house Spec",
        "storage": "Room Temperature",
        "retest_months": 60,
    },
    "PM-PRI-002": {
        "name": "Child-resistant Cap",
        "category": "Primary Packaging",
        "unit": "pcs",
        "spec": "In-house Spec",
        "storage": "Room Temperature",
        "retest_months": 60,
    },
    "PM-LBL-001": {
        "name": "Bottle Label",
        "category": "Labeling",
        "unit": "pcs",
        "spec": "In-house Spec",
        "storage": "Room Temperature",
        "retest_months": 48,
    },
}

# Supplier master data
SUPPLIERS = {
    "SUP-001": {
        "name": "PharmaChem Industries",
        "country": "India",
        "materials": ["RM-API-001"],
        "tier": "Strategic",
    },
    "SUP-002": {
        "name": "ChemPure Ltd",
        "country": "China",
        "materials": ["RM-API-001"],
        "tier": "Approved",
    },
    "SUP-003": {
        "name": "ExcipientCo",
        "country": "Germany",
        "materials": ["RM-EXC-001", "RM-EXC-003"],
        "tier": "Strategic",
    },
    "SUP-004": {
        "name": "PolymerTech",
        "country": "USA",
        "materials": ["RM-EXC-002"],
        "tier": "Approved",
    },
    "SUP-005": {
        "name": "LubeSpec Inc",
        "country": "Japan",
        "materials": ["RM-EXC-004", "RM-EXC-005"],
        "tier": "Approved",
    },
    "SUP-006": {
        "name": "PackWell Solutions",
        "country": "USA",
        "materials": ["PM-PRI-001", "PM-PRI-002"],
        "tier": "Strategic",
    },
    "SUP-007": {
        "name": "PrintPack Ltd",
        "country": "UK",
        "materials": ["PM-SEC-001", "PM-LBL-001"],
        "tier": "Approved",
    },
    "SUP-008": {
        "name": "API Global",
        "country": "India",
        "materials": ["RM-API-001"],
        "tier": "Backup",
    },  # New supplier in 2025
}


def generate_raw_material_receipts(year: int):
    """Generate incoming material receipt and testing records."""
    print(f"\n📦 Generating Raw Material Data for {year}...")

    records = []

    # Generate receipts throughout the year
    for month in range(1, 13):
        # Number of receipts per month varies by material type
        for mat_code, mat_info in MATERIALS.items():
            if "API" in mat_code:
                num_receipts = random.randint(8, 15)  # API received more frequently
            elif "EXC" in mat_code:
                num_receipts = random.randint(4, 8)
            else:
                num_receipts = random.randint(3, 6)

            for _ in range(num_receipts):
                receipt_date = datetime(year, month, random.randint(1, 28))

                # Select supplier
                available_suppliers = [
                    s for s, info in SUPPLIERS.items() if mat_code in info["materials"]
                ]

                # Hidden scenario: New API supplier in Nov 2025
                if mat_code == "RM-API-001" and year == 2025 and month >= 11:
                    if random.random() > 0.6:
                        supplier_id = "SUP-008"  # New supplier
                    else:
                        supplier_id = random.choice(available_suppliers)
                else:
                    if "SUP-008" in available_suppliers and year < 2025:
                        available_suppliers.remove("SUP-008")
                    supplier_id = (
                        random.choice(available_suppliers)
                        if available_suppliers
                        else "SUP-001"
                    )

                supplier_info = SUPPLIERS.get(supplier_id, SUPPLIERS["SUP-001"])

                # Quantity
                if "API" in mat_code:
                    quantity = random.choice([100, 200, 500, 1000])
                elif "EXC" in mat_code:
                    quantity = random.choice([50, 100, 200, 500])
                else:
                    quantity = random.choice([5000, 10000, 20000, 50000])

                # Supplier lot/batch
                supplier_lot = (
                    f"{supplier_id[-3:]}-{year}{month:02d}-{random.randint(1, 99):02d}"
                )

                # COA data
                coa_received = "Yes"
                coa_matches_spec = random.choices(["Yes", "No"], weights=[0.98, 0.02])[
                    0
                ]

                # Hidden scenario: 2022 excipient supplier issue
                if (
                    year == 2022
                    and month in [5, 6, 7]
                    and mat_code in ["RM-EXC-001", "RM-EXC-003"]
                    and supplier_id == "SUP-003"
                ):
                    if random.random() > 0.7:
                        coa_matches_spec = "Borderline"

                # Incoming inspection
                sampling_plan = "ANSI/ASQ Z1.4 Level II"
                sample_size = random.choice([5, 10, 20, 50])

                # Test results
                test_status = (
                    "Pass"
                    if coa_matches_spec == "Yes"
                    else random.choice(["Pass", "Fail", "Conditional"])
                )

                # Hidden scenario: New API supplier quality issues
                if supplier_id == "SUP-008" and year == 2025:
                    if random.random() > 0.85:
                        test_status = "Conditional"

                # Individual test results based on material type
                if "API" in mat_code:
                    identity_test = "Pass"
                    assay_result = round(np.random.normal(99.5, 0.3), 2)
                    if supplier_id == "SUP-008":
                        assay_result = round(
                            np.random.normal(99.2, 0.5), 2
                        )  # Slightly lower, more variable
                    assay_spec = "98.0-102.0%"

                    impurity_total = round(np.random.normal(0.15, 0.03), 3)
                    if supplier_id == "SUP-008":
                        impurity_total = round(
                            np.random.normal(0.22, 0.05), 3
                        )  # Higher impurities
                    impurity_spec = "≤ 0.5%"

                    moisture = round(np.random.normal(0.3, 0.05), 2)
                    moisture_spec = "≤ 0.5%"

                    particle_size_d50 = round(np.random.normal(45, 5), 1)
                    particle_size_spec = "30-60 μm"
                elif "EXC" in mat_code:
                    identity_test = "Pass"
                    assay_result = (
                        round(np.random.normal(99.0, 0.5), 2)
                        if mat_code == "RM-EXC-002"
                        else None
                    )
                    assay_spec = "98.0-102.0%" if assay_result else "N/A"

                    impurity_total = None
                    impurity_spec = "N/A"

                    moisture = (
                        round(np.random.normal(4.0, 0.5), 2)
                        if "MCC" in mat_info["name"]
                        else round(np.random.normal(5.0, 0.5), 2)
                    )
                    moisture_spec = "≤ 5.0%" if "MCC" in mat_info["name"] else "≤ 7.0%"

                    particle_size_d50 = (
                        round(np.random.normal(100, 10), 1)
                        if "MCC" in mat_info["name"]
                        else None
                    )
                    particle_size_spec = "90-120 μm" if particle_size_d50 else "N/A"
                else:
                    identity_test = "Pass"
                    assay_result = None
                    assay_spec = "N/A"
                    impurity_total = None
                    impurity_spec = "N/A"
                    moisture = None
                    moisture_spec = "N/A"
                    particle_size_d50 = None
                    particle_size_spec = "N/A"

                # Microbial testing (for APIs and excipients)
                if "RM" in mat_code:
                    tamc = random.randint(10, 100)
                    tymc = random.randint(5, 50)
                    e_coli = "Absent"
                    salmonella = "Absent"
                else:
                    tamc = None
                    tymc = None
                    e_coli = None
                    salmonella = None

                # Disposition
                if test_status == "Pass":
                    disposition = "Released"
                    disposition_date = receipt_date + timedelta(
                        days=random.randint(3, 7)
                    )
                elif test_status == "Conditional":
                    disposition = random.choice(
                        ["Released with Deviation", "Pending QA Review"]
                    )
                    disposition_date = receipt_date + timedelta(
                        days=random.randint(7, 14)
                    )
                else:
                    disposition = "Rejected"
                    disposition_date = receipt_date + timedelta(
                        days=random.randint(5, 10)
                    )

                # Retest date calculation
                manufacturing_date = receipt_date - timedelta(
                    days=random.randint(30, 180)
                )
                retest_date = manufacturing_date + timedelta(
                    days=mat_info["retest_months"] * 30
                )

                records.append(
                    {
                        "grn_number": f"GRN-{year}-{len(records)+1:05d}",
                        "receipt_date": receipt_date.strftime("%Y-%m-%d"),
                        "material_code": mat_code,
                        "material_name": mat_info["name"],
                        "material_category": mat_info["category"],
                        "supplier_id": supplier_id,
                        "supplier_name": supplier_info["name"],
                        "supplier_country": supplier_info["country"],
                        "supplier_tier": supplier_info["tier"],
                        "supplier_lot": supplier_lot,
                        "manufacturer_lot": f"MFG-{random.randint(1000, 9999)}",
                        "quantity_received": quantity,
                        "unit": mat_info["unit"],
                        "containers_received": random.randint(1, 10),
                        "manufacturing_date": manufacturing_date.strftime("%Y-%m-%d"),
                        "retest_date": retest_date.strftime("%Y-%m-%d"),
                        "storage_condition": mat_info["storage"],
                        "coa_received": coa_received,
                        "coa_matches_spec": coa_matches_spec,
                        "coa_review_by": f"QC-{random.randint(1, 20):02d}",
                        "sampling_plan": sampling_plan,
                        "sample_size": sample_size,
                        "sample_id": f"SAM-{year}-{random.randint(1, 99999):05d}",
                        "identity_test": identity_test,
                        "assay_result_pct": assay_result,
                        "assay_spec": assay_spec,
                        "impurity_total_pct": impurity_total,
                        "impurity_spec": impurity_spec,
                        "moisture_pct": moisture,
                        "moisture_spec": moisture_spec,
                        "particle_size_d50_um": particle_size_d50,
                        "particle_size_spec": particle_size_spec,
                        "tamc_cfu_g": tamc,
                        "tymc_cfu_g": tymc,
                        "e_coli": e_coli,
                        "salmonella": salmonella,
                        "test_status": test_status,
                        "disposition": disposition,
                        "disposition_date": disposition_date.strftime("%Y-%m-%d"),
                        "disposition_by": f"QA-{random.randint(1, 10):02d}",
                        "deviation_raised": (
                            "Yes" if disposition == "Released with Deviation" else "No"
                        ),
                        "deviation_reference": (
                            f"DEV-{year}-{random.randint(1, 500):04d}"
                            if disposition == "Released with Deviation"
                            else ""
                        ),
                        "internal_lot": f"INT-{year}{month:02d}{random.randint(1, 999):03d}",
                        "warehouse_location": f"WH-{random.choice(['A', 'B', 'C'])}-{random.randint(1, 50):02d}",
                        "quarantine_days": (disposition_date - receipt_date).days,
                        "comments": "",
                    }
                )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}raw_materials_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} raw material receipt records")
    return df


def generate_supplier_performance(year: int):
    """Generate supplier performance tracking data."""
    print(f"   📊 Generating Supplier Performance Data for {year}...")

    records = []

    for supplier_id, supplier_info in SUPPLIERS.items():
        # Skip new supplier before 2025
        if supplier_id == "SUP-008" and year < 2025:
            continue

        # Calculate metrics based on receipt data
        num_deliveries = random.randint(20, 100)
        on_time_deliveries = int(num_deliveries * random.uniform(0.85, 0.98))
        quality_rejections = random.randint(0, 3)

        # Hidden scenarios
        if supplier_id == "SUP-003" and year == 2022:
            quality_rejections = random.randint(3, 8)  # More rejections during issue
        if supplier_id == "SUP-008" and year == 2025:
            quality_rejections = random.randint(2, 5)  # New supplier issues

        # Audit information
        last_audit_date = datetime(year, random.randint(1, 12), random.randint(1, 28))
        audit_score = random.randint(70, 100)
        if supplier_id == "SUP-008":
            audit_score = random.randint(65, 80)  # Lower score for new supplier

        records.append(
            {
                "year": year,
                "supplier_id": supplier_id,
                "supplier_name": supplier_info["name"],
                "supplier_country": supplier_info["country"],
                "supplier_tier": supplier_info["tier"],
                "materials_supplied": ", ".join(supplier_info["materials"]),
                "total_deliveries": num_deliveries,
                "on_time_deliveries": on_time_deliveries,
                "otif_rate_pct": round(on_time_deliveries / num_deliveries * 100, 1),
                "late_deliveries": num_deliveries - on_time_deliveries,
                "avg_lead_time_days": random.randint(14, 45),
                "lots_received": num_deliveries,
                "lots_rejected": quality_rejections,
                "quality_acceptance_rate_pct": round(
                    (num_deliveries - quality_rejections) / num_deliveries * 100, 1
                ),
                "coa_discrepancies": random.randint(0, 5),
                "last_audit_date": last_audit_date.strftime("%Y-%m-%d"),
                "audit_type": random.choice(["On-site", "Desktop", "Virtual"]),
                "audit_score": audit_score,
                "audit_classification": (
                    "Approved"
                    if audit_score >= 80
                    else "Conditional" if audit_score >= 70 else "Not Approved"
                ),
                "open_capas": random.randint(0, 3),
                "qualification_status": (
                    "Qualified" if audit_score >= 70 else "Under Review"
                ),
                "qualification_expiry": (
                    last_audit_date + timedelta(days=365)
                ).strftime("%Y-%m-%d"),
                "quality_agreement_status": "Active",
                "total_value_usd": random.randint(50000, 500000),
                "complaints_raised": random.randint(0, 5),
                "response_time_avg_days": random.randint(1, 10),
                "overall_rating": (
                    "A"
                    if audit_score >= 90
                    else "B" if audit_score >= 80 else "C" if audit_score >= 70 else "D"
                ),
                "comments": "",
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}supplier_performance_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} supplier performance records")
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 7")
    print("Raw Material & Supplier Data")
    print("=" * 70)

    all_rm = []
    all_sp = []

    for year in YEARS:
        rm_df = generate_raw_material_receipts(year)
        sp_df = generate_supplier_performance(year)
        if rm_df is not None:
            all_rm.append(rm_df)
        if sp_df is not None:
            all_sp.append(sp_df)

    if all_rm:
        combined_rm = pd.concat(all_rm, ignore_index=True)
        combined_rm.to_csv(f"{OUTPUT_DIR}raw_materials_ALL.csv", index=False)
        print(
            f"\n✅ Combined file: raw_materials_ALL.csv ({len(combined_rm):,} records)"
        )

    if all_sp:
        combined_sp = pd.concat(all_sp, ignore_index=True)
        combined_sp.to_csv(f"{OUTPUT_DIR}supplier_performance_ALL.csv", index=False)
        print(
            f"✅ Combined file: supplier_performance_ALL.csv ({len(combined_sp):,} records)"
        )
