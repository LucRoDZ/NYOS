"""
NYOS APR - Part 5: Customer Complaints & Market Feedback
=========================================================
Product complaints, adverse events, and market returns.
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
OUTPUT_DIR = "/Users/ouzema/Albert School/NYOS/apr_data/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COMPLAINT_CATEGORIES = {
    "Product Quality": [
        "Broken tablets in bottle",
        "Discolored tablets",
        "Chipped tablets",
        "Foreign particle observed",
        "Odor complaint",
        "Tablet too hard to swallow",
        "Wrong tablet count",
        "Packaging damage"
    ],
    "Efficacy": [
        "Product not effective",
        "Delayed onset of action",
        "Duration of effect shorter than expected"
    ],
    "Adverse Event": [
        "Allergic reaction reported",
        "Gastrointestinal upset",
        "Headache after use",
        "Skin rash",
        "Nausea reported"
    ],
    "Labeling": [
        "Missing expiry date",
        "Illegible lot number",
        "Wrong dosage instructions",
        "Missing patient information leaflet"
    ]
}

MARKETS = ["USA", "Canada", "UK", "Germany", "France", "Australia", "Japan", "Brazil", "India", "Mexico"]
DISTRIBUTION_CHANNELS = ["Retail Pharmacy", "Hospital", "Online Pharmacy", "Wholesaler"]


def generate_complaints_data(year: int):
    """
    Generate customer complaints data:
    - Complaint type and severity
    - Linked to specific batches
    - Investigation outcomes
    - Regulatory reporting status
    """
    print(f"\n📞 Generating Customer Complaints Data for {year}...")
    
    # Load manufacturing data to link complaints to batches
    mfg_file = f"{OUTPUT_DIR}manufacturing_extended_{year}.csv"
    if not os.path.exists(mfg_file):
        print(f"   ⚠️  Manufacturing file not found")
        return None
    
    mfg_df = pd.read_csv(mfg_file)
    batch_ids = mfg_df["batch_id"].tolist()
    
    # Complaint rate: ~0.5-1% of batches receive complaints
    num_complaints = int(len(batch_ids) * np.random.uniform(0.005, 0.01))
    
    # Add more complaints during problem periods
    if year == 2025:
        num_complaints = int(num_complaints * 1.3)  # More complaints during supplier issue
    
    records = []
    
    for i in range(num_complaints):
        complaint_date = datetime(year, random.randint(1, 12), random.randint(1, 28))
        
        # Select batch (could be from previous year too)
        if random.random() > 0.1:
            batch_id = random.choice(batch_ids)
        else:
            batch_id = f"PARA-{str(year-1)[-2:]}-{random.randint(1, 7000):04d}"
        
        category = random.choice(list(COMPLAINT_CATEGORIES.keys()))
        description = random.choice(COMPLAINT_CATEGORIES[category])
        
        # Severity classification
        if category == "Adverse Event":
            severity = random.choices(["Critical", "Major", "Minor"], weights=[0.1, 0.4, 0.5])[0]
        elif category == "Product Quality":
            severity = random.choices(["Critical", "Major", "Minor"], weights=[0.05, 0.35, 0.6])[0]
        else:
            severity = random.choices(["Critical", "Major", "Minor"], weights=[0.02, 0.28, 0.7])[0]
        
        # Reporter information
        reporter_type = random.choice(["Patient", "Healthcare Professional", "Pharmacist", "Distributor"])
        
        # Investigation
        investigation_required = "Yes" if severity in ["Critical", "Major"] else random.choice(["Yes", "No"])
        
        if investigation_required == "Yes":
            investigation_start = complaint_date + timedelta(days=random.randint(1, 3))
            investigation_days = random.randint(5, 30) if severity == "Critical" else random.randint(10, 45)
            investigation_complete = investigation_start + timedelta(days=investigation_days)
            
            root_cause = random.choice([
                "Manufacturing process variation",
                "Handling during distribution",
                "Storage conditions",
                "Raw material variation",
                "No defect confirmed - customer handling",
                "Packaging material defect",
                "Equipment issue",
                "Not determined"
            ])
            
            investigation_outcome = random.choice([
                "Confirmed - batch specific",
                "Confirmed - systemic issue",
                "Not confirmed - no defect found",
                "Inconclusive - sample not available"
            ])
        else:
            investigation_start = None
            investigation_complete = None
            root_cause = "N/A - No investigation required"
            investigation_outcome = "N/A"
        
        # Regulatory reporting (for adverse events)
        if category == "Adverse Event" and severity in ["Critical", "Major"]:
            regulatory_reportable = "Yes"
            report_submitted = "Yes" if random.random() > 0.1 else "Pending"
            report_date = complaint_date + timedelta(days=random.randint(1, 15)) if report_submitted == "Yes" else None
        else:
            regulatory_reportable = "No"
            report_submitted = "N/A"
            report_date = None
        
        # CAPA reference (for confirmed issues)
        if investigation_outcome in ["Confirmed - batch specific", "Confirmed - systemic issue"]:
            capa_reference = f"CAPA-{year}-{random.randint(1, 200):04d}"
        else:
            capa_reference = "N/A"
        
        # Customer response
        response_date = complaint_date + timedelta(days=random.randint(1, 5))
        customer_satisfaction = random.choice(["Satisfied", "Neutral", "Dissatisfied"]) if investigation_outcome != "N/A" else "Pending"
        
        records.append({
            "complaint_id": f"COMP-{year}-{i+1:05d}",
            "complaint_date": complaint_date.strftime("%Y-%m-%d"),
            "batch_id": batch_id,
            "category": category,
            "description": description,
            "severity": severity,
            "market": random.choice(MARKETS),
            "distribution_channel": random.choice(DISTRIBUTION_CHANNELS),
            "reporter_type": reporter_type,
            "reporter_contact": fake.email() if reporter_type != "Patient" else "Anonymous",
            "quantity_affected": random.randint(1, 100) if category == "Product Quality" else 1,
            
            # Investigation
            "investigation_required": investigation_required,
            "investigation_start_date": investigation_start.strftime("%Y-%m-%d") if investigation_start else "",
            "investigation_complete_date": investigation_complete.strftime("%Y-%m-%d") if investigation_complete else "",
            "root_cause": root_cause,
            "investigation_outcome": investigation_outcome,
            
            # Regulatory
            "regulatory_reportable": regulatory_reportable,
            "report_submitted": report_submitted,
            "report_date": report_date.strftime("%Y-%m-%d") if report_date else "",
            
            # Actions
            "capa_reference": capa_reference,
            "batch_recall_required": "Yes" if severity == "Critical" and investigation_outcome == "Confirmed - systemic issue" else "No",
            
            # Response
            "initial_response_date": response_date.strftime("%Y-%m-%d"),
            "customer_satisfaction": customer_satisfaction,
            "complaint_status": "Closed" if investigation_outcome != "N/A" and investigation_outcome != "Inconclusive - sample not available" else "Open",
            
            "handled_by": random.choice([f"QA-{i:02d}" for i in range(1, 11)]),
            "comments": ""
        })
    
    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}customer_complaints_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} customer complaint records")
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 5")
    print("Customer Complaints & Market Feedback")
    print("=" * 70)
    
    all_comp = []
    for year in YEARS:
        df = generate_complaints_data(year)
        if df is not None:
            all_comp.append(df)
    
    if all_comp:
        combined = pd.concat(all_comp, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}customer_complaints_ALL.csv", index=False)
        print(f"\n✅ Combined file: customer_complaints_ALL.csv ({len(combined):,} records)")
