"""
NYOS APR Demo - Comprehensive Pharmaceutical Data Generator
============================================================
Generates complete APR (Annual Product Review) data for training LLMs.

Data Categories:
1. Extended Manufacturing Data (Batch Records with full CPPs)
2. Extended QC Lab Data (Complete CQAs and testing)
3. Stability Testing Data (ICH compliant)
4. Environmental Monitoring Data
5. Customer Complaints & Market Feedback
6. CAPA (Corrective and Preventive Actions)
7. Raw Material & Supplier Quality Data
8. Equipment Calibration & Maintenance
9. Batch Release & Disposition Records
10. Training Records
11. Audit Findings

Author: NYOS APR Team
Date: January 2026
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()
Faker.seed(42)

# =============================================================================
# CONFIGURATION
# =============================================================================
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
BATCHES_PER_DAY = 20
MACHINES = ["Press-A", "Press-B", "Press-C"]
OPERATORS = [f"OP-{i:03d}" for i in range(1, 31)]  # 30 operators
GRANULATORS = ["Gran-01", "Gran-02"]
DRYERS = ["FBD-01", "FBD-02", "FBD-03"]
BLENDERS = ["Blend-01", "Blend-02"]
COATING_MACHINES = ["Coat-01", "Coat-02"]

OUTPUT_DIR = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "apr_data") + os.sep
)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================================
# PART 1: EXTENDED MANUFACTURING DATA
# =============================================================================
def generate_extended_manufacturing_data(year: int):
    """
    Generate comprehensive batch manufacturing records with:
    - Full process parameters for each unit operation
    - Operator information
    - Equipment used
    - In-process controls
    - Timing data
    """
    print(f"\n📦 Generating Extended Manufacturing Data for {year}...")

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    total_days = (end_date - start_date).days + 1

    records = []
    batch_index = 1

    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)
        current_month = current_date.month

        # Reduced batches during COVID (2020 March-May)
        if year == 2020 and current_month in [3, 4, 5]:
            daily_batches = random.randint(12, 16)
        else:
            daily_batches = BATCHES_PER_DAY

        for _ in range(daily_batches):
            batch_id = f"PARA-{str(year)[-2:]}-{batch_index:04d}"

            # Shift assignment (Day: 6-14, Evening: 14-22, Night: 22-6)
            shift = random.choices(
                ["Day", "Evening", "Night"], weights=[0.5, 0.35, 0.15]
            )[0]
            if shift == "Day":
                start_hour = random.randint(6, 13)
            elif shift == "Evening":
                start_hour = random.randint(14, 21)
            else:
                start_hour = random.choice([22, 23, 0, 1, 2, 3, 4, 5])

            mfg_start = current_date.replace(
                hour=start_hour, minute=random.randint(0, 59)
            )

            # Equipment assignment
            tablet_press = random.choice(MACHINES)
            granulator = random.choice(GRANULATORS)
            dryer = random.choice(DRYERS)
            blender = random.choice(BLENDERS)

            # Operator assignment
            operator_primary = random.choice(OPERATORS)
            operator_secondary = random.choice(
                [op for op in OPERATORS if op != operator_primary]
            )

            # =====================================================
            # DISPENSING PARAMETERS
            # =====================================================
            api_weight_kg = round(np.random.normal(50.0, 0.5), 3)  # Target: 50kg
            excipient_weight_kg = round(np.random.normal(45.0, 0.4), 3)

            # =====================================================
            # GRANULATION PARAMETERS (Wet Granulation)
            # =====================================================
            granulation_mixing_time_min = round(np.random.normal(15.0, 1.0), 2)
            binder_solution_volume_ml = round(np.random.normal(2500, 100), 1)
            binder_addition_rate_ml_min = round(np.random.normal(50, 5), 2)
            impeller_speed_rpm = round(np.random.normal(150, 10), 0)
            chopper_speed_rpm = round(np.random.normal(1500, 100), 0)
            granulation_endpoint_power_kw = round(np.random.normal(2.5, 0.3), 2)
            granulation_temperature_c = round(np.random.normal(28, 2), 1)

            # =====================================================
            # DRYING PARAMETERS (Fluid Bed Dryer)
            # =====================================================
            inlet_air_temp_c = round(np.random.normal(60, 2), 1)
            outlet_air_temp_c = round(np.random.normal(40, 2), 1)
            drying_time_min = round(np.random.normal(45, 5), 1)
            final_moisture_content_percent = round(np.random.normal(2.0, 0.3), 2)
            airflow_rate_cfm = round(np.random.normal(800, 50), 0)

            # 2024 Summer scenario - higher drying temps
            if year == 2024 and current_month in [7, 8]:
                inlet_air_temp_c = round(np.random.normal(63, 3), 1)
                outlet_air_temp_c = round(np.random.normal(43, 2), 1)

            # =====================================================
            # MILLING PARAMETERS
            # =====================================================
            mill_screen_size_mm = random.choice([0.8, 1.0, 1.5])
            mill_speed_rpm = round(np.random.normal(1200, 100), 0)
            milling_time_min = round(np.random.normal(20, 3), 1)

            # =====================================================
            # BLENDING PARAMETERS
            # =====================================================
            blending_time_min = round(np.random.normal(20, 2), 1)
            blender_speed_rpm = round(np.random.normal(12, 1), 1)
            lubricant_blending_time_min = round(np.random.normal(3, 0.3), 2)
            blend_uniformity_rsd_percent = round(np.random.normal(2.5, 0.5), 2)

            # =====================================================
            # COMPRESSION PARAMETERS
            # =====================================================
            compression_force_main_kn = round(np.random.normal(18.0, 1.5), 2)
            compression_force_pre_kn = round(np.random.normal(3.0, 0.3), 2)
            turret_speed_rpm = round(np.random.normal(45, 3), 1)
            feeder_speed_rpm = round(np.random.normal(25, 2), 1)
            tablet_weight_mg = round(np.random.normal(500, 5), 1)
            tablet_thickness_mm = round(np.random.normal(4.5, 0.1), 2)
            tablet_hardness_n = round(np.random.normal(120, 10), 1)
            friability_percent = round(np.random.exponential(0.3), 3)
            disintegration_time_min = round(np.random.normal(8, 2), 1)

            # 2021 Press-A drift scenario
            if (
                year == 2021
                and current_month in [9, 10, 11]
                and tablet_press == "Press-A"
            ):
                day_in_period = (current_date - datetime(2021, 9, 1)).days
                force_increase = min(day_in_period * 0.03, 3.0)
                compression_force_main_kn = round(
                    np.random.normal(18.0 + force_increase, 1.5), 2
                )

            # 2025 Press-B drift (August 1-15)
            if (
                year == 2025
                and current_date >= datetime(2025, 8, 1)
                and current_date <= datetime(2025, 8, 15)
                and tablet_press == "Press-B"
            ):
                compression_force_main_kn = round(np.random.normal(22.0, 1.0), 2)

            # =====================================================
            # IN-PROCESS CONTROLS (IPC)
            # =====================================================
            ipc_weight_check_pass = (
                "Pass" if abs(tablet_weight_mg - 500) < 25 else "Fail"
            )
            ipc_hardness_check_pass = (
                "Pass" if 100 <= tablet_hardness_n <= 150 else "Fail"
            )
            ipc_thickness_check_pass = (
                "Pass" if 4.2 <= tablet_thickness_mm <= 4.8 else "Fail"
            )
            ipc_friability_check_pass = "Pass" if friability_percent < 1.0 else "Fail"
            ipc_disintegration_check_pass = (
                "Pass" if disintegration_time_min < 15 else "Fail"
            )

            # =====================================================
            # YIELD CALCULATIONS
            # =====================================================
            theoretical_yield_tablets = int(
                (api_weight_kg * 1000) / 500 * 1000
            )  # 500mg tablets
            actual_yield_tablets = int(
                theoretical_yield_tablets * np.random.normal(0.985, 0.01)
            )
            yield_percent = round(
                (actual_yield_tablets / theoretical_yield_tablets) * 100, 2
            )
            yield_percent = max(90.0, min(100.0, yield_percent))

            # Rejects during compression
            reject_count = int(np.random.exponential(50))
            reject_reason = random.choice(
                ["Weight", "Capping", "Sticking", "Chipping", "None"]
            )
            if reject_count < 10:
                reject_reason = "None"

            # =====================================================
            # TIMING DATA
            # =====================================================
            total_process_time_hours = round(np.random.normal(8, 1), 2)
            mfg_end = mfg_start + timedelta(hours=total_process_time_hours)

            # Downtime events
            downtime_minutes = (
                round(np.random.exponential(15), 1) if random.random() < 0.2 else 0
            )
            downtime_reason = (
                random.choice(
                    [
                        "Equipment adjustment",
                        "Tool change",
                        "Material shortage",
                        "Cleaning",
                    ]
                )
                if downtime_minutes > 0
                else "None"
            )

            # =====================================================
            # ENVIRONMENTAL CONDITIONS
            # =====================================================
            room_temperature_c = round(np.random.normal(22, 1), 1)
            room_humidity_percent = round(np.random.normal(45, 5), 1)
            differential_pressure_pa = round(np.random.normal(15, 2), 1)

            # =====================================================
            # BUILD RECORD
            # =====================================================
            records.append(
                {
                    # Identifiers
                    "batch_id": batch_id,
                    "product_name": "Paracetamol 500mg Tablets",
                    "product_code": "PARA-500-TAB",
                    "batch_size_kg": round(api_weight_kg + excipient_weight_kg, 3),
                    # Timing
                    "manufacturing_date": mfg_start.strftime("%Y-%m-%d"),
                    "manufacturing_start_time": mfg_start.strftime("%H:%M"),
                    "manufacturing_end_time": mfg_end.strftime("%H:%M"),
                    "shift": shift,
                    "total_process_time_hours": total_process_time_hours,
                    # Personnel
                    "operator_primary": operator_primary,
                    "operator_secondary": operator_secondary,
                    # Equipment
                    "granulator_id": granulator,
                    "dryer_id": dryer,
                    "blender_id": blender,
                    "tablet_press_id": tablet_press,
                    # Dispensing
                    "api_weight_kg": api_weight_kg,
                    "excipient_weight_kg": excipient_weight_kg,
                    # Granulation
                    "granulation_mixing_time_min": granulation_mixing_time_min,
                    "binder_solution_volume_ml": binder_solution_volume_ml,
                    "binder_addition_rate_ml_min": binder_addition_rate_ml_min,
                    "impeller_speed_rpm": impeller_speed_rpm,
                    "chopper_speed_rpm": chopper_speed_rpm,
                    "granulation_endpoint_power_kw": granulation_endpoint_power_kw,
                    "granulation_temperature_c": granulation_temperature_c,
                    # Drying
                    "inlet_air_temp_c": inlet_air_temp_c,
                    "outlet_air_temp_c": outlet_air_temp_c,
                    "drying_time_min": drying_time_min,
                    "final_moisture_content_percent": final_moisture_content_percent,
                    "airflow_rate_cfm": airflow_rate_cfm,
                    # Milling
                    "mill_screen_size_mm": mill_screen_size_mm,
                    "mill_speed_rpm": mill_speed_rpm,
                    "milling_time_min": milling_time_min,
                    # Blending
                    "blending_time_min": blending_time_min,
                    "blender_speed_rpm": blender_speed_rpm,
                    "lubricant_blending_time_min": lubricant_blending_time_min,
                    "blend_uniformity_rsd_percent": blend_uniformity_rsd_percent,
                    # Compression
                    "compression_force_main_kn": compression_force_main_kn,
                    "compression_force_pre_kn": compression_force_pre_kn,
                    "turret_speed_rpm": turret_speed_rpm,
                    "feeder_speed_rpm": feeder_speed_rpm,
                    "tablet_weight_mg": tablet_weight_mg,
                    "tablet_thickness_mm": tablet_thickness_mm,
                    "tablet_hardness_n": tablet_hardness_n,
                    "friability_percent": friability_percent,
                    "disintegration_time_min": disintegration_time_min,
                    # IPC Results
                    "ipc_weight_check": ipc_weight_check_pass,
                    "ipc_hardness_check": ipc_hardness_check_pass,
                    "ipc_thickness_check": ipc_thickness_check_pass,
                    "ipc_friability_check": ipc_friability_check_pass,
                    "ipc_disintegration_check": ipc_disintegration_check_pass,
                    # Yield
                    "theoretical_yield_tablets": theoretical_yield_tablets,
                    "actual_yield_tablets": actual_yield_tablets,
                    "yield_percent": yield_percent,
                    "reject_count": reject_count,
                    "reject_reason": reject_reason,
                    # Downtime
                    "downtime_minutes": downtime_minutes,
                    "downtime_reason": downtime_reason,
                    # Environment
                    "room_temperature_c": room_temperature_c,
                    "room_humidity_percent": room_humidity_percent,
                    "differential_pressure_pa": differential_pressure_pa,
                }
            )

            batch_index += 1

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}manufacturing_extended_{year}.csv", index=False)
    print(
        f"   ✓ Generated {len(df):,} extended manufacturing records ({len(df.columns)} columns)"
    )
    return df


# =============================================================================
# MAIN EXECUTION - PART 1
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 1")
    print("Extended Manufacturing Data")
    print("=" * 70)

    all_mfg = []
    for year in YEARS:
        df = generate_extended_manufacturing_data(year)
        all_mfg.append(df)

    # Combine all years
    combined = pd.concat(all_mfg, ignore_index=True)
    combined.to_csv(f"{OUTPUT_DIR}manufacturing_extended_ALL.csv", index=False)
    print(
        f"\n✅ Combined file: manufacturing_extended_ALL.csv ({len(combined):,} records)"
    )
    print(f"   Columns: {len(combined.columns)}")
