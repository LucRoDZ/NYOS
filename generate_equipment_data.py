"""
NYOS APR - Part 8: Equipment Calibration & Maintenance
=======================================================
Calibration records, preventive maintenance, equipment qualification.
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

# Equipment master data
EQUIPMENT = {
    # Manufacturing Equipment
    "GR-001": {
        "name": "High Shear Granulator HSG-500",
        "type": "Granulator",
        "location": "GR-101",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": [
            "Impeller Speed",
            "Chopper Speed",
            "Load Cell",
            "Temperature Sensor",
        ],
    },
    "GR-002": {
        "name": "High Shear Granulator HSG-500",
        "type": "Granulator",
        "location": "GR-101",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": [
            "Impeller Speed",
            "Chopper Speed",
            "Load Cell",
            "Temperature Sensor",
        ],
    },
    "DR-001": {
        "name": "Fluid Bed Dryer FBD-200",
        "type": "Dryer",
        "location": "DR-101",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": [
            "Inlet Air Temperature",
            "Outlet Air Temperature",
            "Air Flow",
            "Product Temperature",
        ],
    },
    "DR-002": {
        "name": "Fluid Bed Dryer FBD-200",
        "type": "Dryer",
        "location": "DR-101",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": [
            "Inlet Air Temperature",
            "Outlet Air Temperature",
            "Air Flow",
            "Product Temperature",
        ],
    },
    "DR-003": {
        "name": "Tray Dryer TD-100",
        "type": "Dryer",
        "location": "DR-101",
        "criticality": "Medium",
        "calibration_freq_months": 12,
        "pm_freq_months": 6,
        "parameters": ["Chamber Temperature", "Air Velocity"],
    },
    "ML-001": {
        "name": "Oscillating Granulator OG-200",
        "type": "Mill",
        "location": "ML-101",
        "criticality": "Medium",
        "calibration_freq_months": 12,
        "pm_freq_months": 6,
        "parameters": ["Screen Size Verification", "Motor Speed"],
    },
    "BL-001": {
        "name": "V-Blender VB-500",
        "type": "Blender",
        "location": "BL-101",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": ["Rotation Speed", "Timer", "Intensifier Bar Speed"],
    },
    "BL-002": {
        "name": "Double Cone Blender DCB-500",
        "type": "Blender",
        "location": "BL-101",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": ["Rotation Speed", "Timer"],
    },
    "PRESS-A": {
        "name": "Rotary Tablet Press RTP-45",
        "type": "Tablet Press",
        "location": "CP-101",
        "criticality": "Critical",
        "calibration_freq_months": 3,
        "pm_freq_months": 1,
        "parameters": [
            "Pre-compression Force",
            "Main Compression Force",
            "Turret Speed",
            "Weight Control System",
            "Hardness Monitor",
        ],
    },
    "PRESS-B": {
        "name": "Rotary Tablet Press RTP-45",
        "type": "Tablet Press",
        "location": "CP-101",
        "criticality": "Critical",
        "calibration_freq_months": 3,
        "pm_freq_months": 1,
        "parameters": [
            "Pre-compression Force",
            "Main Compression Force",
            "Turret Speed",
            "Weight Control System",
            "Hardness Monitor",
        ],
    },
    "PRESS-C": {
        "name": "Rotary Tablet Press RTP-45",
        "type": "Tablet Press",
        "location": "CP-102",
        "criticality": "Critical",
        "calibration_freq_months": 3,
        "pm_freq_months": 1,
        "parameters": [
            "Pre-compression Force",
            "Main Compression Force",
            "Turret Speed",
            "Weight Control System",
            "Hardness Monitor",
        ],
    },
    # QC Equipment
    "HPLC-001": {
        "name": "HPLC System Agilent 1260",
        "type": "HPLC",
        "location": "QC-LAB",
        "criticality": "Critical",
        "calibration_freq_months": 12,
        "pm_freq_months": 6,
        "parameters": [
            "Pump Flow Rate",
            "UV Detector Wavelength",
            "Column Oven Temperature",
            "Autosampler Precision",
        ],
    },
    "HPLC-002": {
        "name": "HPLC System Waters 2695",
        "type": "HPLC",
        "location": "QC-LAB",
        "criticality": "Critical",
        "calibration_freq_months": 12,
        "pm_freq_months": 6,
        "parameters": [
            "Pump Flow Rate",
            "UV Detector Wavelength",
            "Column Oven Temperature",
            "Autosampler Precision",
        ],
    },
    "DISS-001": {
        "name": "Dissolution Apparatus USP-II",
        "type": "Dissolution Tester",
        "location": "QC-LAB",
        "criticality": "Critical",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": [
            "Paddle Speed",
            "Temperature",
            "Vessel Position",
            "Sampling Probe Position",
        ],
    },
    "DISS-002": {
        "name": "Dissolution Apparatus USP-II",
        "type": "Dissolution Tester",
        "location": "QC-LAB",
        "criticality": "Critical",
        "calibration_freq_months": 6,
        "pm_freq_months": 3,
        "parameters": [
            "Paddle Speed",
            "Temperature",
            "Vessel Position",
            "Sampling Probe Position",
        ],
    },
    "BAL-001": {
        "name": "Analytical Balance Mettler XS205",
        "type": "Balance",
        "location": "QC-LAB",
        "criticality": "Critical",
        "calibration_freq_months": 6,
        "pm_freq_months": 12,
        "parameters": ["Linearity", "Repeatability", "Eccentricity", "Sensitivity"],
    },
    "BAL-002": {
        "name": "Analytical Balance Mettler XS205",
        "type": "Balance",
        "location": "QC-LAB",
        "criticality": "Critical",
        "calibration_freq_months": 6,
        "pm_freq_months": 12,
        "parameters": ["Linearity", "Repeatability", "Eccentricity", "Sensitivity"],
    },
    "BAL-003": {
        "name": "Top Loading Balance Mettler MS6002S",
        "type": "Balance",
        "location": "MFG",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 12,
        "parameters": ["Linearity", "Repeatability", "Eccentricity"],
    },
    "HARD-001": {
        "name": "Hardness Tester Erweka TBH-325",
        "type": "Hardness Tester",
        "location": "QC-LAB",
        "criticality": "High",
        "calibration_freq_months": 6,
        "pm_freq_months": 12,
        "parameters": ["Force Accuracy", "Force Repeatability"],
    },
    "FRIA-001": {
        "name": "Friability Tester Erweka TA-20",
        "type": "Friability Tester",
        "location": "QC-LAB",
        "criticality": "High",
        "calibration_freq_months": 12,
        "pm_freq_months": 12,
        "parameters": ["Rotation Speed", "Timer"],
    },
    "DISINT-001": {
        "name": "Disintegration Tester Erweka ZT-322",
        "type": "Disintegration Tester",
        "location": "QC-LAB",
        "criticality": "High",
        "calibration_freq_months": 12,
        "pm_freq_months": 12,
        "parameters": ["Temperature", "Cycle Rate"],
    },
    "FTIR-001": {
        "name": "FTIR Spectrometer Thermo Nicolet",
        "type": "FTIR",
        "location": "QC-LAB",
        "criticality": "High",
        "calibration_freq_months": 12,
        "pm_freq_months": 12,
        "parameters": ["Wavelength Accuracy", "Resolution", "Noise Level"],
    },
    "UV-001": {
        "name": "UV-Vis Spectrophotometer Shimadzu",
        "type": "UV-Vis",
        "location": "QC-LAB",
        "criticality": "High",
        "calibration_freq_months": 12,
        "pm_freq_months": 12,
        "parameters": ["Wavelength Accuracy", "Photometric Accuracy", "Stray Light"],
    },
    "KF-001": {
        "name": "Karl Fischer Titrator Metrohm",
        "type": "KF Titrator",
        "location": "QC-LAB",
        "criticality": "High",
        "calibration_freq_months": 12,
        "pm_freq_months": 12,
        "parameters": ["Electrode Response", "Titrant Factor"],
    },
}


def generate_calibration_records(year: int):
    """Generate equipment calibration records."""
    print(f"\n🔧 Generating Equipment Calibration Data for {year}...")

    records = []

    for eq_id, eq_info in EQUIPMENT.items():
        # Number of calibrations per year based on frequency
        num_calibrations = 12 // eq_info["calibration_freq_months"]

        for cal_num in range(num_calibrations):
            # Calculate scheduled date
            month = (cal_num * eq_info["calibration_freq_months"]) + random.randint(
                1, eq_info["calibration_freq_months"]
            )
            month = min(month, 12)

            scheduled_date = datetime(year, month, random.randint(1, 28))

            # Actual calibration might be +/- few days
            actual_date = scheduled_date + timedelta(days=random.randint(-3, 7))

            # Hidden scenario: Press-A drift in 2021
            if eq_id == "PRESS-A" and year == 2021 and month >= 9:
                force_drift = True
            else:
                force_drift = False

            # Hidden scenario: Press-B drift in 2025
            if eq_id == "PRESS-B" and year == 2025 and month >= 8:
                press_b_drift = True
            else:
                press_b_drift = False

            # Generate results for each parameter
            for param in eq_info["parameters"]:
                # Determine if parameter passes or fails
                if force_drift and "Force" in param:
                    pass_probability = 0.7  # Higher failure rate
                elif press_b_drift and "Force" in param:
                    pass_probability = 0.75
                else:
                    pass_probability = 0.97

                result = "Pass" if random.random() < pass_probability else "Fail"

                # Measurement values
                if "Temperature" in param:
                    setpoint = random.choice([25.0, 37.0, 40.0, 50.0, 60.0])
                    tolerance = 0.5
                    measured = round(np.random.normal(setpoint, tolerance / 3), 2)
                    if force_drift or press_b_drift:
                        measured = round(measured + random.uniform(0.3, 0.8), 2)
                    unit = "°C"
                elif "Force" in param:
                    setpoint = random.choice([5.0, 10.0, 15.0, 20.0, 30.0])
                    tolerance = setpoint * 0.02
                    measured = round(np.random.normal(setpoint, tolerance / 3), 2)
                    if force_drift:
                        measured = round(measured + random.uniform(0.3, 0.8), 2)
                    elif press_b_drift:
                        measured = round(measured + random.uniform(0.2, 0.6), 2)
                    unit = "kN"
                elif "Speed" in param or "RPM" in param:
                    setpoint = random.choice([50, 100, 150, 200, 300])
                    tolerance = setpoint * 0.02
                    measured = round(np.random.normal(setpoint, tolerance / 3), 1)
                    unit = "RPM"
                elif "Flow" in param:
                    setpoint = random.choice([1.0, 2.0, 5.0, 10.0])
                    tolerance = setpoint * 0.02
                    measured = round(np.random.normal(setpoint, tolerance / 3), 3)
                    unit = "mL/min"
                elif "Wavelength" in param:
                    setpoint = random.choice([254, 280, 486, 656])
                    tolerance = 1.0
                    measured = round(np.random.normal(setpoint, tolerance / 3), 1)
                    unit = "nm"
                else:
                    setpoint = 100.0
                    tolerance = 2.0
                    measured = round(np.random.normal(setpoint, tolerance / 3), 2)
                    unit = "%"

                # Adjustment required?
                deviation = abs(measured - setpoint)
                adjustment_required = "Yes" if deviation > tolerance * 0.5 else "No"

                # As-found vs as-left
                as_found = measured
                if adjustment_required == "Yes" and result != "Fail":
                    as_left = round(setpoint + np.random.normal(0, tolerance / 6), 2)
                else:
                    as_left = as_found

                records.append(
                    {
                        "calibration_id": f"CAL-{year}-{len(records)+1:05d}",
                        "equipment_id": eq_id,
                        "equipment_name": eq_info["name"],
                        "equipment_type": eq_info["type"],
                        "location": eq_info["location"],
                        "criticality": eq_info["criticality"],
                        "parameter": param,
                        "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                        "actual_date": actual_date.strftime("%Y-%m-%d"),
                        "next_due_date": (
                            actual_date
                            + timedelta(days=eq_info["calibration_freq_months"] * 30)
                        ).strftime("%Y-%m-%d"),
                        "setpoint": setpoint,
                        "tolerance": tolerance,
                        "unit": unit,
                        "as_found_value": as_found,
                        "as_left_value": as_left,
                        "deviation": round(deviation, 3),
                        "result": result,
                        "adjustment_required": adjustment_required,
                        "reference_standard": f"STD-{random.randint(1, 50):03d}",
                        "standard_certificate": f"CERT-{random.randint(10000, 99999)}",
                        "standard_traceable": (
                            "NIST"
                            if eq_info["criticality"] == "Critical"
                            else "Manufacturer"
                        ),
                        "calibrated_by": f"CAL-{random.randint(1, 10):02d}",
                        "verified_by": f"QA-{random.randint(1, 10):02d}",
                        "out_of_tolerance": "Yes" if result == "Fail" else "No",
                        "oot_investigation": (
                            f"OOT-{year}-{random.randint(1, 50):03d}"
                            if result == "Fail"
                            else ""
                        ),
                        "impact_assessment": "Required" if result == "Fail" else "N/A",
                        "comments": "",
                    }
                )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}equipment_calibration_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} calibration records")
    return df


def generate_maintenance_records(year: int):
    """Generate preventive maintenance records."""
    print(f"   🔩 Generating Preventive Maintenance Data for {year}...")

    records = []

    for eq_id, eq_info in EQUIPMENT.items():
        # Number of PM per year based on frequency
        num_pms = 12 // eq_info["pm_freq_months"]

        for pm_num in range(num_pms):
            month = (pm_num * eq_info["pm_freq_months"]) + 1
            month = min(month, 12)

            scheduled_date = datetime(year, month, random.randint(1, 28))
            actual_date = scheduled_date + timedelta(days=random.randint(-5, 10))

            # PM activities based on equipment type
            if eq_info["type"] == "Tablet Press":
                activities = [
                    "Punch and die inspection",
                    "Turret alignment check",
                    "Force feeder adjustment",
                    "Lubrication of moving parts",
                    "Electrical connections check",
                    "Safety interlocks verification",
                ]
            elif eq_info["type"] == "HPLC":
                activities = [
                    "Pump seal replacement",
                    "Detector lamp check",
                    "Autosampler needle inspection",
                    "Column compartment cleaning",
                    "System suitability verification",
                ]
            elif eq_info["type"] in ["Granulator", "Blender"]:
                activities = [
                    "Seal inspection and replacement",
                    "Motor bearing check",
                    "Electrical connections inspection",
                    "Safety interlocks verification",
                    "Product contact surface inspection",
                ]
            elif eq_info["type"] == "Dryer":
                activities = [
                    "Filter bag inspection",
                    "Heater element check",
                    "Air handling unit inspection",
                    "Temperature sensor verification",
                    "Product retention screen check",
                ]
            else:
                activities = [
                    "General inspection",
                    "Cleaning verification",
                    "Functional check",
                    "Documentation review",
                ]

            selected_activities = random.sample(
                activities, min(len(activities), random.randint(3, 5))
            )

            # Parts replaced
            parts_replaced = random.choices(
                ["None", "Seals", "Filters", "Bearings", "Belts", "Multiple"],
                weights=[0.5, 0.2, 0.15, 0.08, 0.05, 0.02],
            )[0]

            # PM result
            pm_result = random.choices(
                ["Pass", "Pass with observations", "Fail - repair required"],
                weights=[0.8, 0.15, 0.05],
            )[0]

            # Downtime
            if pm_result == "Fail - repair required":
                downtime_hours = random.randint(4, 48)
            else:
                downtime_hours = random.randint(1, 4)

            records.append(
                {
                    "pm_id": f"PM-{year}-{len(records)+1:05d}",
                    "equipment_id": eq_id,
                    "equipment_name": eq_info["name"],
                    "equipment_type": eq_info["type"],
                    "location": eq_info["location"],
                    "criticality": eq_info["criticality"],
                    "pm_type": "Preventive",
                    "scheduled_date": scheduled_date.strftime("%Y-%m-%d"),
                    "actual_date": actual_date.strftime("%Y-%m-%d"),
                    "next_due_date": (
                        actual_date + timedelta(days=eq_info["pm_freq_months"] * 30)
                    ).strftime("%Y-%m-%d"),
                    "activities_performed": "; ".join(selected_activities),
                    "parts_replaced": parts_replaced,
                    "parts_cost_usd": (
                        random.randint(0, 2000) if parts_replaced != "None" else 0
                    ),
                    "result": pm_result,
                    "observations": (
                        f"Minor {random.choice(['wear', 'corrosion', 'buildup'])} observed"
                        if "observations" in pm_result
                        else ""
                    ),
                    "follow_up_required": "Yes" if pm_result != "Pass" else "No",
                    "follow_up_ref": (
                        f"WO-{year}-{random.randint(1, 500):04d}"
                        if pm_result != "Pass"
                        else ""
                    ),
                    "downtime_hours": downtime_hours,
                    "performed_by": f"MAINT-{random.randint(1, 15):02d}",
                    "verified_by": f"ENG-{random.randint(1, 5):02d}",
                    "labor_hours": random.uniform(1, 8),
                    "total_cost_usd": random.randint(100, 5000),
                    "comments": "",
                }
            )

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}preventive_maintenance_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} preventive maintenance records")
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 8")
    print("Equipment Calibration & Maintenance")
    print("=" * 70)

    all_cal = []
    all_pm = []

    for year in YEARS:
        cal_df = generate_calibration_records(year)
        pm_df = generate_maintenance_records(year)
        if cal_df is not None:
            all_cal.append(cal_df)
        if pm_df is not None:
            all_pm.append(pm_df)

    if all_cal:
        combined_cal = pd.concat(all_cal, ignore_index=True)
        combined_cal.to_csv(f"{OUTPUT_DIR}equipment_calibration_ALL.csv", index=False)
        print(
            f"\n✅ Combined file: equipment_calibration_ALL.csv ({len(combined_cal):,} records)"
        )

    if all_pm:
        combined_pm = pd.concat(all_pm, ignore_index=True)
        combined_pm.to_csv(f"{OUTPUT_DIR}preventive_maintenance_ALL.csv", index=False)
        print(
            f"✅ Combined file: preventive_maintenance_ALL.csv ({len(combined_pm):,} records)"
        )
