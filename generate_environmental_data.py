"""
NYOS APR - Part 4: Environmental Monitoring Data
=================================================
Clean room monitoring: viable and non-viable particles, temperature, humidity.
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

# Manufacturing areas
ROOMS = {
    "GR-101": {"name": "Granulation Room", "class": "ISO 8", "type": "Processing"},
    "DR-101": {"name": "Drying Room", "class": "ISO 8", "type": "Processing"},
    "BL-101": {"name": "Blending Room", "class": "ISO 8", "type": "Processing"},
    "CP-101": {"name": "Compression Room 1", "class": "ISO 8", "type": "Processing"},
    "CP-102": {"name": "Compression Room 2", "class": "ISO 8", "type": "Processing"},
    "PK-101": {"name": "Primary Packaging", "class": "ISO 8", "type": "Packaging"},
    "WH-101": {"name": "Warehouse - RM", "class": "Controlled", "type": "Storage"},
    "WH-102": {"name": "Warehouse - FG", "class": "Controlled", "type": "Storage"},
    "QC-LAB": {"name": "QC Laboratory", "class": "ISO 7", "type": "Laboratory"},
    "MICRO-LAB": {"name": "Microbiology Lab", "class": "ISO 7", "type": "Laboratory"},
}

# Sampling locations within rooms
SAMPLING_POINTS = ["SP-01", "SP-02", "SP-03", "SP-04", "SP-05"]


def generate_environmental_data(year: int):
    """
    Generate environmental monitoring data:
    - Non-viable particle counts (0.5µm, 5.0µm)
    - Viable air sampling (settle plates, active air)
    - Temperature and humidity
    - Differential pressure
    """
    print(f"\n🌡️ Generating Environmental Monitoring Data for {year}...")
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    records = []
    record_id = 1
    
    current_date = start_date
    while current_date <= end_date:
        # Environmental monitoring typically done during production shifts
        for room_code, room_info in ROOMS.items():
            # Number of sampling points per room
            num_points = random.randint(2, 4)
            selected_points = random.sample(SAMPLING_POINTS, num_points)
            
            for sp in selected_points:
                # Sample time (typically morning and afternoon)
                sample_times = ["09:00", "14:00"] if random.random() > 0.3 else ["09:00"]
                
                for sample_time in sample_times:
                    # ISO class limits
                    if room_info["class"] == "ISO 7":
                        limit_05um = 352000
                        limit_50um = 2930
                        limit_viable = 10  # CFU/m³
                    elif room_info["class"] == "ISO 8":
                        limit_05um = 3520000
                        limit_50um = 29300
                        limit_viable = 100
                    else:  # Controlled
                        limit_05um = 10000000
                        limit_50um = 100000
                        limit_viable = 200
                    
                    # Generate particle counts (particles/m³)
                    particles_05um = int(np.random.lognormal(np.log(limit_05um * 0.3), 0.5))
                    particles_50um = int(np.random.lognormal(np.log(limit_50um * 0.2), 0.5))
                    
                    # Viable counts (CFU/m³ for active air, CFU/plate for settle plates)
                    viable_active_air = int(np.random.exponential(limit_viable * 0.2))
                    viable_settle_plate = int(np.random.exponential(3))
                    
                    # Temperature (Spec: 18-25°C typically)
                    base_temp = 22.0
                    if year == 2024 and current_date.month in [7, 8]:
                        base_temp = 24.0  # Summer heat impact
                    temperature_c = round(np.random.normal(base_temp, 1.0), 1)
                    
                    # Humidity (Spec: 30-65% RH typically)
                    humidity_percent = round(np.random.normal(45, 8), 1)
                    
                    # Differential pressure (Spec: >10 Pa positive)
                    diff_pressure_pa = round(np.random.normal(15, 2), 1)
                    
                    # Determine results
                    particle_05_result = "Pass" if particles_05um <= limit_05um else "Excursion"
                    particle_50_result = "Pass" if particles_50um <= limit_50um else "Excursion"
                    viable_result = "Pass" if viable_active_air <= limit_viable else "Alert" if viable_active_air <= limit_viable * 1.5 else "Action"
                    temp_result = "Pass" if 18.0 <= temperature_c <= 25.0 else "Excursion"
                    humidity_result = "Pass" if 30.0 <= humidity_percent <= 65.0 else "Excursion"
                    pressure_result = "Pass" if diff_pressure_pa >= 10.0 else "Excursion"
                    
                    overall = "Pass" if all([
                        particle_05_result == "Pass",
                        particle_50_result == "Pass",
                        viable_result == "Pass",
                        temp_result == "Pass",
                        humidity_result == "Pass",
                        pressure_result == "Pass"
                    ]) else "Excursion"
                    
                    records.append({
                        "record_id": f"EM-{year}-{record_id:06d}",
                        "monitoring_date": current_date.strftime("%Y-%m-%d"),
                        "monitoring_time": sample_time,
                        "room_code": room_code,
                        "room_name": room_info["name"],
                        "room_classification": room_info["class"],
                        "room_type": room_info["type"],
                        "sampling_point": sp,
                        
                        # Non-viable particles
                        "particles_05um_per_m3": particles_05um,
                        "particles_05um_limit": limit_05um,
                        "particles_05um_result": particle_05_result,
                        "particles_50um_per_m3": particles_50um,
                        "particles_50um_limit": limit_50um,
                        "particles_50um_result": particle_50_result,
                        
                        # Viable monitoring
                        "viable_active_air_cfu_m3": viable_active_air,
                        "viable_active_limit": limit_viable,
                        "viable_settle_plate_cfu": viable_settle_plate,
                        "viable_result": viable_result,
                        
                        # Physical parameters
                        "temperature_c": temperature_c,
                        "temp_spec": "18.0 - 25.0°C",
                        "temp_result": temp_result,
                        "humidity_percent_rh": humidity_percent,
                        "humidity_spec": "30.0 - 65.0% RH",
                        "humidity_result": humidity_result,
                        "differential_pressure_pa": diff_pressure_pa,
                        "pressure_spec": "≥10.0 Pa",
                        "pressure_result": pressure_result,
                        
                        "overall_result": overall,
                        "technician_id": random.choice([f"ENV-{i:02d}" for i in range(1, 11)]),
                        "comments": "" if overall == "Pass" else "Investigation initiated"
                    })
                    record_id += 1
        
        current_date += timedelta(days=1)
    
    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}environmental_monitoring_{year}.csv", index=False)
    print(f"   ✓ Generated {len(df):,} environmental monitoring records")
    return df


if __name__ == "__main__":
    print("=" * 70)
    print("NYOS APR - Comprehensive Data Generator - PART 4")
    print("Environmental Monitoring Data")
    print("=" * 70)
    
    all_env = []
    for year in YEARS:
        df = generate_environmental_data(year)
        if df is not None:
            all_env.append(df)
    
    if all_env:
        combined = pd.concat(all_env, ignore_index=True)
        combined.to_csv(f"{OUTPUT_DIR}environmental_monitoring_ALL.csv", index=False)
        print(f"\n✅ Combined file: environmental_monitoring_ALL.csv ({len(combined):,} records)")
