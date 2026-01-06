import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_batches(n_batches=500):
    print(f"Generating {n_batches} batch records...")
    records = []
    start_date = datetime(2024, 1, 1)
    machines = ["Press-A", "Press-B", "Press-C"]
    operators = [f"OP-{i:03d}" for i in range(1, 20)]

    for i in range(n_batches):
        date = start_date + timedelta(days=i // 10)
        machine = random.choice(machines)

        base_hardness = 85 if machine == "Press-A" else 88
        if machine == "Press-A" and date > datetime(2024, 9, 1):
            base_hardness += (date - datetime(2024, 9, 1)).days * 0.05

        records.append(
            {
                "batch_id": f"PARA-24-{i+1:04d}",
                "product_name": "Paracetamol 500mg",
                "manufacturing_date": date.strftime("%Y-%m-%d"),
                "machine": machine,
                "operator": random.choice(operators),
                "compression_force": round(random.gauss(20, 1.5), 2),
                "hardness": round(random.gauss(base_hardness, 5), 1),
                "weight": round(random.gauss(500, 3), 1),
                "thickness": round(random.gauss(4.0, 0.1), 2),
                "yield_percent": round(min(100, max(92, random.gauss(98, 1.5))), 1),
                "status": "released",
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/batches.csv", index=False)
    print(f"  -> {OUTPUT_DIR}/batches.csv")
    return df


def generate_qc_results(batches_df):
    print("Generating QC results...")
    records = []

    for _, batch in batches_df.iterrows():
        result = "pass"
        dissolution = random.gauss(95, 3)
        if dissolution < 85:
            result = "fail"

        records.append(
            {
                "batch_id": batch["batch_id"],
                "test_date": batch["manufacturing_date"],
                "dissolution": round(dissolution, 1),
                "assay": round(random.gauss(99, 1), 1),
                "hardness": round(random.gauss(batch["hardness"], 2), 1),
                "friability": round(max(0, random.gauss(0.3, 0.1)), 2),
                "disintegration": round(max(0, random.gauss(8, 2)), 1),
                "uniformity": round(random.gauss(1.5, 0.3), 2),
                "result": result,
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/qc_results.csv", index=False)
    print(f"  -> {OUTPUT_DIR}/qc_results.csv")
    return df


def generate_complaints(n=30):
    print(f"Generating {n} complaints...")
    categories = [
        "Packaging",
        "Efficacy",
        "Foreign matter",
        "Tablet defect",
        "Labeling",
    ]
    severities = ["low", "medium", "high", "critical"]

    records = []
    for i in range(n):
        date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        records.append(
            {
                "complaint_id": f"CMP-2024-{i+1:04d}",
                "date": date.strftime("%Y-%m-%d"),
                "batch_id": f"PARA-24-{random.randint(1, 500):04d}",
                "category": random.choice(categories),
                "severity": random.choices(severities, weights=[0.5, 0.3, 0.15, 0.05])[
                    0
                ],
                "description": f"Customer complaint regarding {random.choice(categories).lower()}",
                "status": random.choices(
                    ["open", "closed", "investigating"], weights=[0.3, 0.5, 0.2]
                )[0],
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/complaints.csv", index=False)
    print(f"  -> {OUTPUT_DIR}/complaints.csv")
    return df


def generate_capas(n=15):
    print(f"Generating {n} CAPAs...")
    sources = ["Complaint", "Audit", "Deviation", "OOS", "Self-inspection"]
    types = ["corrective", "preventive"]
    statuses = ["open", "closed", "in-progress"]

    records = []
    for i in range(n):
        date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        records.append(
            {
                "capa_id": f"CAPA-2024-{i+1:04d}",
                "date": date.strftime("%Y-%m-%d"),
                "type": random.choice(types),
                "source": random.choice(sources),
                "description": f"CAPA initiated due to {random.choice(sources).lower()} finding",
                "root_cause": (
                    "Root cause analysis pending"
                    if random.random() > 0.6
                    else "Identified: Process deviation"
                ),
                "status": statuses[i % 3],
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/capas.csv", index=False)
    print(f"  -> {OUTPUT_DIR}/capas.csv")
    return df


def generate_equipment(n=10):
    print(f"Generating {n} equipment records...")
    equipment_list = [
        ("Press-A", "Tablet Press"),
        ("Press-B", "Tablet Press"),
        ("Press-C", "Tablet Press"),
        ("Gran-01", "Granulator"),
        ("Gran-02", "Granulator"),
        ("FBD-01", "Fluid Bed Dryer"),
        ("FBD-02", "Fluid Bed Dryer"),
        ("Blend-01", "Blender"),
        ("Blend-02", "Blender"),
        ("Coat-01", "Coating Machine"),
    ]

    records = []
    today = datetime(2024, 12, 15)
    for i, (eq_id, eq_name) in enumerate(equipment_list[:n]):
        last_cal = today - timedelta(days=random.randint(30, 180))
        next_cal = last_cal + timedelta(days=random.randint(85, 95))
        status = "due" if next_cal <= today + timedelta(days=7) else "ok"

        records.append(
            {
                "equipment_id": eq_id,
                "name": eq_name,
                "calibration_date": last_cal.strftime("%Y-%m-%d"),
                "next_calibration": next_cal.strftime("%Y-%m-%d"),
                "status": status,
                "parameter": "Force" if "Press" in eq_id else "Temperature",
                "deviation": round(random.gauss(0, 0.5), 2),
            }
        )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/equipment.csv", index=False)
    print(f"  -> {OUTPUT_DIR}/equipment.csv")
    return df


if __name__ == "__main__":
    print("=" * 50)
    print("NYOS Sample Data Generator")
    print("=" * 50)
    batches = generate_batches(500)
    generate_qc_results(batches)
    generate_complaints(30)
    generate_capas(15)
    generate_equipment(10)
    print("=" * 50)
    print("Done! Import these CSV files via the NYOS web interface.")
