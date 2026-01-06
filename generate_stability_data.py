"""
NYOS APR - Part 3: Stability Testing Data (ICH Compliant)
=========================================================
Long-term, accelerated, and intermediate stability studies per ICH Q1A(R2).
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

# Stability conditions per ICH
STABILITY_CONDITIONS = {
    "Long-term": {
        "temp_c": 25,
        "rh_percent": 60,
        "timepoints": [0, 3, 6, 9, 12, 18, 24, 36],
    },
    "Accelerated": {"temp_c": 40, "rh_percent": 75, "timepoints": [0, 3, 6]},
    "Intermediate": {"temp_c": 30, "rh_percent": 65, "timepoints": [0, 6, 9, 12]},
}


def generate_stability_data(year: int):
    """
    Generate ICH-compliant stability data for ~5% of batches per year.
    Tests: Assay, Dissolution, Impurities, Water content, Appearance, Hardness
    """
    print(f"\n📊 Generating Stability Testing Data for {year}...")

    # Load manufacturing data to get batch IDs
    mfg_file = f"{OUTPUT_DIR}manufacturing_extended_{year}.csv"
    if not os.path.exists(mfg_file):
        print(f"   ⚠️  Manufacturing file not found")
        return None

    mfg_df = pd.read_csv(mfg_file)

    # Select ~5% of batches for stability (annual stability batches)
    num_stability_batches = max(10, int(len(mfg_df) * 0.05))
    stability_batches = mfg_df.sample(n=num_stability_batches, random_state=year)

    records = []
    study_id = 1

    for _, batch_row in stability_batches.iterrows():
        batch_id = batch_row["batch_id"]
        mfg_date = datetime.strptime(batch_row["manufacturing_date"], "%Y-%m-%d")

        # Each batch goes into multiple stability conditions
        for condition, params in STABILITY_CONDITIONS.items():
            study_code = f"STAB-{year}-{study_id:04d}"

            # Baseline values (T=0)
            baseline_assay = round(np.random.normal(100.0, 1.0), 2)
            baseline_dissolution = round(np.random.normal(93.0, 2.0), 1)
            baseline_impurity_a = round(np.random.exponential(0.04), 4)
            baseline_total_impurities = round(
                baseline_impurity_a + np.random.exponential(0.08), 4
            )
            baseline_water_content = round(np.random.normal(2.0, 0.2), 3)
            baseline_hardness = round(np.random.normal(120, 8), 1)

            for timepoint in params["timepoints"]:
                test_date = mfg_date + timedelta(
                    days=timepoint * 30
                )  # Approximate months

                # Simulate degradation over time
                time_factor = timepoint / 36  # Normalized to max timepoint

                # Assay decreases slightly over time
                if condition == "Accelerated":
                    assay_decrease = time_factor * np.random.uniform(1.5, 3.0)
                elif condition == "Intermediate":
                    assay_decrease = time_factor * np.random.uniform(0.8, 1.5)
                else:  # Long-term
                    assay_decrease = time_factor * np.random.uniform(0.3, 0.8)

                assay = round(
                    baseline_assay - assay_decrease + np.random.normal(0, 0.3), 2
                )

                # Dissolution may decrease
                if condition == "Accelerated":
                    diss_decrease = time_factor * np.random.uniform(2, 5)
                else:
                    diss_decrease = time_factor * np.random.uniform(0.5, 2)
                dissolution = round(
                    baseline_dissolution - diss_decrease + np.random.normal(0, 1), 1
                )
                dissolution = max(75, min(100, dissolution))

                # Impurities increase over time
                if condition == "Accelerated":
                    impurity_increase = time_factor * np.random.uniform(0.02, 0.05)
                else:
                    impurity_increase = time_factor * np.random.uniform(0.005, 0.02)
                impurity_a = round(baseline_impurity_a + impurity_increase, 4)
                total_impurities = round(
                    baseline_total_impurities + impurity_increase * 2, 4
                )

                # Water content may increase
                water_increase = (
                    time_factor * np.random.uniform(0.1, 0.3)
                    if condition == "Accelerated"
                    else time_factor * np.random.uniform(0.02, 0.1)
                )
                water_content = round(baseline_water_content + water_increase, 3)

                # Hardness may change
                hardness_change = time_factor * np.random.uniform(-5, 5)
                hardness = round(baseline_hardness + hardness_change, 1)

                # Appearance
                if assay < 95 or total_impurities > 0.4:
                    appearance = random.choice(
                        ["Slightly yellow tablets", "Discolored tablets"]
                    )
                else:
                    appearance = "White to off-white, round, biconvex tablets"

                # Determine pass/fail
                assay_result = "Pass" if 95.0 <= assay <= 105.0 else "Fail"
                dissolution_result = "Pass" if dissolution >= 80.0 else "Fail"
                impurity_result = (
                    "Pass"
                    if impurity_a <= 0.10 and total_impurities <= 0.50
                    else "Fail"
                )
                water_result = "Pass" if water_content <= 3.0 else "Fail"
                appearance_result = (
                    "Conforms" if "Discolored" not in appearance else "Does Not Conform"
                )

                overall = (
                    "Pass"
                    if all(
                        [
                            assay_result == "Pass",
                            dissolution_result == "Pass",
                            impurity_result == "Pass",
                            water_result == "Pass",
                            appearance_result == "Conforms",
                        ]
                    )
                    else "Fail"
                )

                records.append(
                    {
                        "study_id": study_code,
                        "batch_id": batch_id,
                        "stability_condition": condition,
                        "storage_temp_c": params["temp_c"],
                        "storage_rh_percent": params["rh_percent"],
                        "timepoint_months": timepoint,
                        "test_date": test_date.strftime("%Y-%m-%d"),
                        "manufacturing_date": mfg_date.strftime("%Y-%m-%d"),
                        # Results
                        "appearance": appearance,
                        "appearance_result": appearance_result,
                        "assay_percent": assay,
                        "assay_spec": "95.0 - 105.0%",
                        "assay_result": assay_result,
                        "dissolution_30min_percent": dissolution,
                        "dissolution_spec": "NLT 80% (Q)",
                        "dissolution_result": dissolution_result,
                        "impurity_a_percent": impurity_a,
                        "impurity_a_spec": "NMT 0.10%",
                        "total_impurities_percent": total_impurities,
                        "total_impurities_spec": "NMT 0.50%",
                        "impurity_result": impurity_result,
                        "water_content_percent": water_content,
                        "water_spec": "NMT 3.0%",
                        "water_result": water_result,
                        "hardness_n": hardness,
                        "hardness_spec": "100 - 150 N",
                        "overall_result": overall,
                        "analyst_id": random.choice(
                            [f"QC-{i:03d}" for i in range(1, 21)]
                        ),
                        "reviewed_by": random.choice(
                            [f"QC-{i:03d}" for i in range(1, 5)]
                        ),
                        "comments": (
                            ""
                            if overall == "Pass"
                            else (
                                "OOS investigation initiated"
                                if random.random() > 0.5
                                else "Trend monitoring required"
                            )
                        ),
                    }
                )

            study_id += 1

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}stability_data_{year}.csv", index=False)
    print(
        f"   ✓ Generated {len(df):,} stability test records for {num_stability_batches} batches"
    )
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 3")
    print("Stability Testing Data (ICH Compliant)")
    print("=" * 70)

    all_stab = []
    for year in YEARS:
        df = generate_stability_data(year)
        if df is not None:
            all_stab.append(df)

    if all_stab:
        combined = pd.concat(all_stab, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}stability_data_ALL.csv", index=False)
        print(f"\n✅ Combined file: stability_data_ALL.csv ({len(combined):,} records)")
