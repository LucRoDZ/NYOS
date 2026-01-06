"""
NYOS APR - Part 2: Extended QC Lab Data
=======================================
Complete quality control testing data per ICH/FDA guidelines.
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

ANALYSTS = [f"QC-{i:03d}" for i in range(1, 21)]  # 20 QC analysts
HPLC_SYSTEMS = ["HPLC-01", "HPLC-02", "HPLC-03", "HPLC-04"]
UV_SYSTEMS = ["UV-01", "UV-02"]
DISSOLUTION_APPARATUS = ["Diss-01", "Diss-02", "Diss-03"]
HARDNESS_TESTERS = ["Hard-01", "Hard-02"]
FRIABILITY_TESTERS = ["Fria-01"]
MOISTURE_ANALYZERS = ["Karl-01", "Karl-02"]


def generate_extended_qc_data(year: int):
    """
    Generate comprehensive QC lab data including:
    - All CQA tests with full details
    - Equipment used
    - Analyst information
    - Method references
    - Raw data values
    - System suitability
    """
    print(f"\n🔬 Generating Extended QC Lab Data for {year}...")
    
    # Load manufacturing data to get batch IDs
    mfg_file = f"{OUTPUT_DIR}manufacturing_extended_{year}.csv"
    if not os.path.exists(mfg_file):
        print(f"   ⚠️  Manufacturing file not found: {mfg_file}")
        return None
    
    mfg_df = pd.read_csv(mfg_file)
    
    records = []
    
    for _, mfg_row in mfg_df.iterrows():
        batch_id = mfg_row["batch_id"]
        mfg_date = datetime.strptime(mfg_row["manufacturing_date"], "%Y-%m-%d")
        current_month = mfg_date.month
        tablet_press = mfg_row["tablet_press_id"]
        
        # Testing typically done 1-3 days after manufacturing
        test_date = mfg_date + timedelta(days=random.randint(1, 3))
        
        # Assign analysts
        analyst_chemical = random.choice(ANALYSTS)
        analyst_physical = random.choice([a for a in ANALYSTS if a != analyst_chemical])
        analyst_micro = random.choice(ANALYSTS)
        
        # =================================================================
        # IDENTIFICATION TESTS
        # =================================================================
        id_ir_result = "Conforms" if random.random() > 0.001 else "Does Not Conform"
        id_hplc_rt_min = round(np.random.normal(8.5, 0.1), 3)  # Retention time
        id_hplc_result = "Conforms" if 8.0 <= id_hplc_rt_min <= 9.0 else "Does Not Conform"
        
        # =================================================================
        # ASSAY (HPLC)
        # =================================================================
        hplc_system = random.choice(HPLC_SYSTEMS)
        
        # System suitability
        sst_tailing_factor = round(np.random.normal(1.1, 0.05), 3)
        sst_theoretical_plates = int(np.random.normal(8000, 500))
        sst_rsd_percent = round(np.random.exponential(0.5), 3)
        sst_pass = "Pass" if (sst_tailing_factor < 2.0 and sst_theoretical_plates > 2000 and sst_rsd_percent < 2.0) else "Fail"
        
        # Assay result (Spec: 95.0-105.0%)
        # Apply year-specific scenarios
        if year == 2023 and current_month in [4, 5, 6]:
            # Lab method transition - slight positive bias
            assay_percent = round(np.random.normal(101.5, 1.5), 2)
        else:
            assay_percent = round(np.random.normal(100.0, 1.5), 2)
        
        # Individual injection values (6 injections)
        assay_injections = [round(assay_percent + np.random.normal(0, 0.3), 2) for _ in range(6)]
        assay_rsd = round(np.std(assay_injections) / np.mean(assay_injections) * 100, 3)
        
        assay_result = "Pass" if 95.0 <= assay_percent <= 105.0 else "Fail"
        
        # =================================================================
        # DISSOLUTION TESTING (USP Apparatus II)
        # =================================================================
        diss_apparatus = random.choice(DISSOLUTION_APPARATUS)
        diss_medium = "Phosphate Buffer pH 5.8"
        diss_volume_ml = 900
        diss_rpm = 50
        diss_temp_c = round(np.random.normal(37.0, 0.2), 1)
        
        # Individual vessel results at 30 min (Spec: Q=80%, each ≥Q+5%=85%)
        # Apply scenarios
        is_drifting_batch = (year == 2025 and 
                           mfg_date >= datetime(2025, 8, 1) and 
                           mfg_date <= datetime(2025, 8, 15) and 
                           tablet_press == "Press-B")
        
        is_excipient_issue = (year == 2022 and current_month == 6)
        
        if is_drifting_batch:
            diss_mean = 81.0
            diss_std = 1.5
        elif is_excipient_issue:
            diss_mean = 88.0
            diss_std = 6.0
        else:
            diss_mean = 92.0
            diss_std = 3.0
        
        diss_vessel_1 = round(np.random.normal(diss_mean, diss_std), 1)
        diss_vessel_2 = round(np.random.normal(diss_mean, diss_std), 1)
        diss_vessel_3 = round(np.random.normal(diss_mean, diss_std), 1)
        diss_vessel_4 = round(np.random.normal(diss_mean, diss_std), 1)
        diss_vessel_5 = round(np.random.normal(diss_mean, diss_std), 1)
        diss_vessel_6 = round(np.random.normal(diss_mean, diss_std), 1)
        
        # Clamp values
        diss_vessels = [max(70, min(100, v)) for v in [diss_vessel_1, diss_vessel_2, diss_vessel_3, 
                                                        diss_vessel_4, diss_vessel_5, diss_vessel_6]]
        diss_30min_mean = round(np.mean(diss_vessels), 1)
        diss_30min_min = min(diss_vessels)
        diss_30min_rsd = round(np.std(diss_vessels) / np.mean(diss_vessels) * 100, 2)
        
        # S1 criteria: Each unit ≥ Q+5% (85%)
        diss_s1_pass = all(v >= 85 for v in diss_vessels)
        diss_result = "Pass" if diss_s1_pass else "Fail"
        
        # =================================================================
        # CONTENT UNIFORMITY (USP <905>)
        # =================================================================
        cu_mean = 100.0
        cu_std = 2.0
        cu_values = [round(np.random.normal(cu_mean, cu_std), 1) for _ in range(10)]
        cu_average = round(np.mean(cu_values), 2)
        cu_rsd = round(np.std(cu_values) / np.mean(cu_values) * 100, 2)
        cu_av = round(abs(cu_average - 100) + 2.4 * np.std(cu_values), 2)  # Acceptance Value
        cu_result = "Pass" if cu_av <= 15.0 else "Fail"
        
        # =================================================================
        # RELATED SUBSTANCES / IMPURITIES (HPLC)
        # =================================================================
        # Impurity A (Spec: ≤0.10%)
        if year == 2025 and current_month == 11:
            # November supplier issue
            impurity_a = round(np.random.exponential(0.09), 4)
        else:
            impurity_a = round(np.random.exponential(0.05), 4)
        impurity_a = max(0.001, min(0.15, impurity_a))
        
        # Impurity B (4-Aminophenol) (Spec: ≤0.005%)
        impurity_b = round(np.random.exponential(0.002), 4)
        impurity_b = max(0.0001, min(0.01, impurity_b))
        
        # Impurity C (Spec: ≤0.05%)
        impurity_c = round(np.random.exponential(0.02), 4)
        impurity_c = max(0.001, min(0.08, impurity_c))
        
        # Any unknown impurity (Spec: ≤0.10%)
        unknown_max_impurity = round(np.random.exponential(0.03), 4)
        
        # Total impurities (Spec: ≤0.50%)
        total_impurities = round(impurity_a + impurity_b + impurity_c + unknown_max_impurity + 
                                 np.random.exponential(0.05), 4)
        total_impurities = min(0.6, total_impurities)
        
        impurities_result = "Pass" if (impurity_a <= 0.10 and impurity_b <= 0.005 and 
                                       impurity_c <= 0.05 and total_impurities <= 0.50) else "Fail"
        
        # =================================================================
        # PHYSICAL TESTS
        # =================================================================
        hardness_tester = random.choice(HARDNESS_TESTERS)
        
        # Hardness (Spec: 100-150 N)
        # Apply scenarios
        if year == 2021 and current_month in [9, 10, 11] and tablet_press == "Press-A":
            day_in_period = (mfg_date - datetime(2021, 9, 1)).days
            hardness_increase = min(day_in_period * 0.15, 15.0)
            hardness_mean = 120.0 + hardness_increase
        else:
            hardness_mean = 120.0
        
        hardness_values = [round(np.random.normal(hardness_mean, 10), 1) for _ in range(10)]
        hardness_mean_result = round(np.mean(hardness_values), 1)
        hardness_min = min(hardness_values)
        hardness_max = max(hardness_values)
        hardness_result = "Pass" if all(100 <= h <= 150 for h in hardness_values) else "Fail"
        
        # Friability (Spec: ≤1.0%)
        friability_tester = random.choice(FRIABILITY_TESTERS)
        friability_initial_wt_g = round(np.random.normal(6.5, 0.1), 3)
        friability_final_wt_g = round(friability_initial_wt_g * (1 - np.random.exponential(0.003)), 3)
        friability_percent = round((friability_initial_wt_g - friability_final_wt_g) / friability_initial_wt_g * 100, 3)
        friability_result = "Pass" if friability_percent <= 1.0 else "Fail"
        
        # Disintegration (Spec: ≤15 min)
        disintegration_times = [round(np.random.normal(8, 2), 1) for _ in range(6)]
        disintegration_max = max(disintegration_times)
        disintegration_result = "Pass" if disintegration_max <= 15.0 else "Fail"
        
        # Weight Variation (Spec: ±5% of label claim)
        weight_values = [round(np.random.normal(500, 5), 1) for _ in range(20)]
        weight_mean = round(np.mean(weight_values), 1)
        weight_rsd = round(np.std(weight_values) / np.mean(weight_values) * 100, 2)
        weight_min = min(weight_values)
        weight_max = max(weight_values)
        weight_result = "Pass" if all(475 <= w <= 525 for w in weight_values) else "Fail"
        
        # =================================================================
        # MOISTURE CONTENT (Karl Fischer)
        # =================================================================
        moisture_analyzer = random.choice(MOISTURE_ANALYZERS)
        moisture_percent = round(np.random.normal(2.0, 0.3), 3)
        moisture_percent = max(0.5, min(4.0, moisture_percent))
        moisture_result = "Pass" if moisture_percent <= 3.0 else "Fail"
        
        # =================================================================
        # MICROBIAL LIMITS (USP <61>, <62>)
        # =================================================================
        tamc_cfu_g = int(np.random.exponential(50))  # Spec: ≤1000 CFU/g
        tymc_cfu_g = int(np.random.exponential(20))  # Spec: ≤100 CFU/g
        e_coli = "Absent" if random.random() > 0.001 else "Present"
        salmonella = "Absent"
        s_aureus = "Absent" if random.random() > 0.001 else "Present"
        p_aeruginosa = "Absent" if random.random() > 0.001 else "Present"
        
        micro_result = "Pass" if (tamc_cfu_g <= 1000 and tymc_cfu_g <= 100 and 
                                  e_coli == "Absent" and salmonella == "Absent") else "Fail"
        
        # =================================================================
        # OVERALL BATCH RESULT
        # =================================================================
        all_tests = [assay_result, diss_result, cu_result, impurities_result,
                     hardness_result, friability_result, disintegration_result,
                     weight_result, moisture_result, micro_result]
        overall_result = "Pass" if all(t == "Pass" for t in all_tests) else "Fail"
        
        # =================================================================
        # BUILD RECORD
        # =================================================================
        records.append({
            # Identifiers
            "batch_id": batch_id,
            "sample_id": f"QC-{batch_id}",
            "test_date": test_date.strftime("%Y-%m-%d"),
            
            # Analysts
            "analyst_chemical": analyst_chemical,
            "analyst_physical": analyst_physical,
            "analyst_micro": analyst_micro,
            
            # Identification
            "id_ir_result": id_ir_result,
            "id_hplc_rt_min": id_hplc_rt_min,
            "id_hplc_result": id_hplc_result,
            
            # Assay
            "hplc_system": hplc_system,
            "sst_tailing_factor": sst_tailing_factor,
            "sst_theoretical_plates": sst_theoretical_plates,
            "sst_rsd_percent": sst_rsd_percent,
            "sst_result": sst_pass,
            "assay_percent": assay_percent,
            "assay_injection_1": assay_injections[0],
            "assay_injection_2": assay_injections[1],
            "assay_injection_3": assay_injections[2],
            "assay_injection_4": assay_injections[3],
            "assay_injection_5": assay_injections[4],
            "assay_injection_6": assay_injections[5],
            "assay_rsd_percent": assay_rsd,
            "assay_result": assay_result,
            
            # Dissolution
            "dissolution_apparatus": diss_apparatus,
            "dissolution_medium": diss_medium,
            "dissolution_volume_ml": diss_volume_ml,
            "dissolution_rpm": diss_rpm,
            "dissolution_temp_c": diss_temp_c,
            "dissolution_vessel_1": diss_vessels[0],
            "dissolution_vessel_2": diss_vessels[1],
            "dissolution_vessel_3": diss_vessels[2],
            "dissolution_vessel_4": diss_vessels[3],
            "dissolution_vessel_5": diss_vessels[4],
            "dissolution_vessel_6": diss_vessels[5],
            "dissolution_30min_mean": diss_30min_mean,
            "dissolution_30min_min": diss_30min_min,
            "dissolution_30min_rsd": diss_30min_rsd,
            "dissolution_result": diss_result,
            
            # Content Uniformity
            "cu_value_1": cu_values[0],
            "cu_value_2": cu_values[1],
            "cu_value_3": cu_values[2],
            "cu_value_4": cu_values[3],
            "cu_value_5": cu_values[4],
            "cu_value_6": cu_values[5],
            "cu_value_7": cu_values[6],
            "cu_value_8": cu_values[7],
            "cu_value_9": cu_values[8],
            "cu_value_10": cu_values[9],
            "cu_average": cu_average,
            "cu_rsd_percent": cu_rsd,
            "cu_acceptance_value": cu_av,
            "cu_result": cu_result,
            
            # Impurities
            "impurity_a_percent": impurity_a,
            "impurity_b_percent": impurity_b,
            "impurity_c_percent": impurity_c,
            "unknown_max_impurity_percent": unknown_max_impurity,
            "total_impurities_percent": total_impurities,
            "impurities_result": impurities_result,
            
            # Physical Tests
            "hardness_tester": hardness_tester,
            "hardness_mean_n": hardness_mean_result,
            "hardness_min_n": hardness_min,
            "hardness_max_n": hardness_max,
            "hardness_result": hardness_result,
            
            "friability_tester": friability_tester,
            "friability_initial_wt_g": friability_initial_wt_g,
            "friability_final_wt_g": friability_final_wt_g,
            "friability_percent": friability_percent,
            "friability_result": friability_result,
            
            "disintegration_max_min": disintegration_max,
            "disintegration_result": disintegration_result,
            
            "weight_mean_mg": weight_mean,
            "weight_rsd_percent": weight_rsd,
            "weight_min_mg": weight_min,
            "weight_max_mg": weight_max,
            "weight_result": weight_result,
            
            # Moisture
            "moisture_analyzer": moisture_analyzer,
            "moisture_percent": moisture_percent,
            "moisture_result": moisture_result,
            
            # Microbial
            "tamc_cfu_g": tamc_cfu_g,
            "tymc_cfu_g": tymc_cfu_g,
            "e_coli": e_coli,
            "salmonella": salmonella,
            "s_aureus": s_aureus,
            "p_aeruginosa": p_aeruginosa,
            "micro_result": micro_result,
            
            # Overall
            "overall_result": overall_result,
        })
    
    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}qc_lab_extended_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} extended QC records ({len(df.columns)} columns)")
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 2")
    print("Extended QC Lab Data")
    print("=" * 70)
    
    all_qc = []
    for year in YEARS:
        df = generate_extended_qc_data(year)
        if df is not None:
            all_qc.append(df)
    
    if all_qc:
        combined = pd.concat(all_qc, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}qc_lab_extended_ALL.csv", index=False)
        print(f"\n✅ Combined file: qc_lab_extended_ALL.csv ({len(combined):,} records)")
        print(f"   Columns: {len(combined.columns)}")
