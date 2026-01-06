"""
NYOS APR - Master Data Index & Summary
=======================================
Overview of all generated datasets and hidden scenarios documentation.
"""

import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "apr_data") + os.sep
)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_data_summary():
    """Generate a comprehensive summary of all APR datasets."""

    print("=" * 80)
    print("NYOS APR - COMPREHENSIVE DATA GENERATION SUMMARY")
    print("Product: Paracetamol 500mg Tablets (PARA-500-TAB)")
    print("Time Period: 2020-2025 (6 years)")
    print("=" * 80)

    datasets = []

    # List all CSV files
    files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".csv")])

    total_records = 0
    total_columns = 0

    print("\n📊 DATASET INVENTORY")
    print("-" * 80)

    for f in files:
        filepath = os.path.join(OUTPUT_DIR, f)
        df = pd.read_csv(filepath)
        records = len(df)
        columns = len(df.columns)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)

        total_records += records
        total_columns += columns

        datasets.append(
            {
                "filename": f,
                "records": records,
                "columns": columns,
                "size_mb": round(size_mb, 2),
            }
        )

        print(
            f"  {f:45} | {records:>8,} records | {columns:>3} cols | {size_mb:>6.2f} MB"
        )

    print("-" * 80)
    print(f"  {'TOTAL':45} | {total_records:>8,} records")

    # Create summary dataframe
    summary_df = pd.DataFrame(datasets)
    summary_df.to_csv(f"{OUTPUT_DIR}_data_index.csv", index=False)

    return summary_df


def document_hidden_scenarios():
    """Document all hidden scenarios embedded in the data for AI detection."""

    scenarios = [
        {
            "year": 2020,
            "scenario": "COVID-19 Impact",
            "description": "Reduced production capacity March-May 2020, higher process variability due to supply chain disruptions",
            "datasets_affected": ["manufacturing_extended", "qc_extended"],
            "indicators": [
                "Reduced batch count in Q2",
                "Higher CPP variability",
                "Extended manufacturing times",
            ],
            "detection_difficulty": "Medium",
        },
        {
            "year": 2021,
            "scenario": "Tablet Press-A Degradation",
            "description": "Press-A showing gradual degradation Sept-Nov 2021, manifesting as increased hardness variability",
            "datasets_affected": [
                "manufacturing_extended",
                "qc_extended",
                "equipment_calibration",
            ],
            "indicators": [
                "Gradual increase in hardness values for Press-A batches",
                "Higher compression force variability",
                "Calibration failures on force parameters",
            ],
            "detection_difficulty": "Medium-Hard",
        },
        {
            "year": 2022,
            "scenario": "Excipient Supplier Quality Issue",
            "description": "MCC supplier (SUP-003) quality issues in June 2022 causing dissolution variability",
            "datasets_affected": [
                "qc_extended",
                "raw_materials",
                "supplier_performance",
                "capa_records",
            ],
            "indicators": [
                "Increased dissolution variability June-July",
                "Higher rejection rate for MCC lots",
                "Borderline COA results",
                "Increased CAPA count",
            ],
            "detection_difficulty": "Medium",
        },
        {
            "year": 2023,
            "scenario": "Analytical Method Transition",
            "description": "Lab method update in Q2 2023 causing temporary positive bias in assay results",
            "datasets_affected": ["qc_extended"],
            "indicators": [
                "Systematic assay increase April-June",
                "Higher SST %RSD values",
                "Return to normal in Q3",
            ],
            "detection_difficulty": "Hard",
        },
        {
            "year": 2024,
            "scenario": "Seasonal Environmental Effect",
            "description": "July-August 2024 showing higher drying temperatures due to HVAC limitations",
            "datasets_affected": ["manufacturing_extended", "environmental_monitoring"],
            "indicators": [
                "Higher drying endpoint temperatures",
                "Environmental excursions in drying rooms",
                "Potential moisture content variation",
            ],
            "detection_difficulty": "Easy-Medium",
        },
        {
            "year": 2025,
            "scenario": "Multiple Issues - Press-B Drift & API Supplier Change",
            "description": "Press-B showing drift Aug 1-15, 2025; New API supplier (SUP-008) introduced Nov 2025 with higher impurity profile",
            "datasets_affected": [
                "manufacturing_extended",
                "qc_extended",
                "raw_materials",
                "supplier_performance",
            ],
            "indicators": [
                "Press-B compression force drift",
                "New supplier code appearing in November",
                "Higher total impurity results",
                "Lower assay results from new supplier",
            ],
            "detection_difficulty": "Medium",
        },
        {
            "year": "All Years",
            "scenario": "Missed Deviations",
            "description": "Approximately 20 batches per year with low yield (<95%) but no corresponding deviation record",
            "datasets_affected": ["manufacturing_extended", "batch_release"],
            "indicators": [
                "Low yield batches without deviation reference",
                "Released batches with yield <95%",
                "Mismatch between yield issues and deviation count",
            ],
            "detection_difficulty": "Medium",
        },
    ]

    print("\n" + "=" * 80)
    print("🔍 HIDDEN SCENARIOS FOR AI DETECTION")
    print("=" * 80)

    for s in scenarios:
        print(f"\n📌 {s['year']}: {s['scenario']}")
        print(f"   Description: {s['description']}")
        print(f"   Detection Difficulty: {s['detection_difficulty']}")
        print(f"   Datasets: {', '.join(s['datasets_affected'])}")
        print(f"   Key Indicators:")
        for ind in s["indicators"]:
            print(f"      • {ind}")

    # Save scenarios documentation
    scenarios_df = pd.DataFrame(scenarios)
    scenarios_df.to_csv(f"{OUTPUT_DIR}_hidden_scenarios.csv", index=False)

    return scenarios_df


def generate_apr_kpis():
    """Generate key APR metrics summary."""

    print("\n" + "=" * 80)
    print("📈 KEY APR METRICS (2020-2025)")
    print("=" * 80)

    metrics = []

    for year in range(2020, 2026):
        # Load data for each year
        try:
            mfg_df = pd.read_csv(f"{OUTPUT_DIR}manufacturing_extended_{year}.csv")
            qc_df = pd.read_csv(f"{OUTPUT_DIR}qc_lab_extended_{year}.csv")
            release_df = pd.read_csv(f"{OUTPUT_DIR}batch_release_{year}.csv")
            comp_df = pd.read_csv(f"{OUTPUT_DIR}customer_complaints_{year}.csv")
            capa_df = pd.read_csv(f"{OUTPUT_DIR}capa_records_{year}.csv")

            # Calculate metrics
            batches = len(mfg_df)
            released = len(release_df[release_df["disposition"] == "Released"])
            rejected = len(release_df[release_df["disposition"] == "Rejected"])
            release_rate = round(released / batches * 100, 1)

            avg_yield = (
                round(mfg_df["actual_yield_pct"].mean(), 1)
                if "actual_yield_pct" in mfg_df.columns
                else "N/A"
            )

            complaints = len(comp_df)
            critical_capas = len(capa_df[capa_df["risk_score"] == "Critical"])

            metrics.append(
                {
                    "year": year,
                    "batches_manufactured": batches,
                    "batches_released": released,
                    "batches_rejected": rejected,
                    "release_rate_pct": release_rate,
                    "avg_yield_pct": avg_yield,
                    "complaints": complaints,
                    "critical_capas": critical_capas,
                }
            )

            print(f"\n{year}:")
            print(
                f"   Batches: {batches:,} | Released: {released:,} ({release_rate}%) | Rejected: {rejected}"
            )
            print(
                f"   Avg Yield: {avg_yield}% | Complaints: {complaints} | Critical CAPAs: {critical_capas}"
            )

        except FileNotFoundError:
            print(f"\n{year}: Data files not found")

    # Save metrics
    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv(f"{OUTPUT_DIR}_apr_kpis.csv", index=False)

    return metrics_df


def create_readme():
    """Create README file for the dataset."""

    readme = """# NYOS APR Synthetic Data - Paracetamol 500mg Tablets

## Overview
This dataset contains comprehensive synthetic pharmaceutical Annual Product Review (APR) data
for **Paracetamol 500mg Tablets** covering the period **2020-2025**.

## Purpose
- Training LLMs for pharmaceutical data analysis
- Demonstrating NYOS APR AI platform capabilities
- Testing AI-driven trend detection and anomaly identification

## Product Information
- **Product Name:** Paracetamol 500mg Tablets
- **Product Code:** PARA-500-TAB
- **Batch ID Format:** PARA-YY-XXXX (e.g., PARA-25-0001)
- **Batch Size:** 200 kg
- **Shelf Life:** 36 months

## Datasets Included

### Manufacturing Data
- `manufacturing_extended_YYYY.csv` - Complete manufacturing records with CPPs (60 columns)
- Includes: Dispensing, Granulation, Drying, Milling, Blending, Compression, IPC data

### Quality Control Data
- `qc_extended_YYYY.csv` - Complete QC testing results with CQAs (86 columns)
- Includes: Identification, Assay, Dissolution, Content Uniformity, Impurities, Physical tests

### Stability Data
- `stability_testing_YYYY.csv` - ICH-compliant stability studies
- Conditions: Long-term (25°C/60%RH), Accelerated (40°C/75%RH), Intermediate (30°C/65%RH)

### Environmental Monitoring
- `environmental_monitoring_YYYY.csv` - Clean room monitoring data
- Parameters: Particle counts, viable monitoring, temperature, humidity, differential pressure

### Customer Complaints
- `customer_complaints_YYYY.csv` - Market feedback and complaint records
- Categories: Product Quality, Efficacy, Adverse Events, Labeling

### CAPA Records
- `capa_records_YYYY.csv` - Corrective and Preventive Action tracking
- Linked to deviations, complaints, audit findings

### Raw Materials
- `raw_materials_YYYY.csv` - Incoming material receipts and testing
- `supplier_performance_YYYY.csv` - Supplier qualification and tracking

### Equipment
- `equipment_calibration_YYYY.csv` - Calibration records
- `preventive_maintenance_YYYY.csv` - PM records

### Batch Release
- `batch_release_YYYY.csv` - QP release decisions and disposition

## Hidden Scenarios (For AI Detection)

The data contains embedded scenarios for AI to detect:

1. **2020 - COVID Impact**: Reduced production March-May, higher variability
2. **2021 - Press-A Degradation**: Sept-Nov hardness increase
3. **2022 - Excipient Supplier Issue**: June dissolution variability from MCC supplier
4. **2023 - Lab Method Transition**: Q2 assay positive bias
5. **2024 - Seasonal Effect**: July-Aug higher drying temps
6. **2025 - Multiple Issues**: Press-B drift (Aug) + New API supplier (Nov)
7. **All Years - Missed Deviations**: ~20 low yield batches without logged deviations

## Standards Compliance
- ICH Q1A(R2) - Stability Testing
- ICH Q2(R1) - Analytical Validation
- ICH Q3A/B - Impurities
- ICH Q7 - GMP for APIs
- ISO 14644 - Cleanroom Standards
- USP <905>, <711>, <621> - Testing Methods

## Data Quality Notes
- All batch IDs are unique and traceable
- Timestamps are realistic and sequential
- Linked records maintain referential integrity
- Statistical distributions match typical pharmaceutical operations

## Usage
```python
import pandas as pd

# Load all data for a specific year
mfg_2024 = pd.read_csv('apr_data/manufacturing_extended_2024.csv')
qc_2024 = pd.read_csv('apr_data/qc_extended_2024.csv')

# Load combined multi-year data
all_mfg = pd.read_csv('apr_data/manufacturing_extended_ALL.csv')
all_qc = pd.read_csv('apr_data/qc_extended_ALL.csv')
```

## Generation Date
Generated: {date}

## Version
v1.0 - Comprehensive APR Data Package
""".format(
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    with open(f"{OUTPUT_DIR}README.md", "w") as f:
        f.write(readme)

    print("\n✅ README.md created")


if __name__ == "__main__":
    summary = generate_data_summary()
    scenarios = document_hidden_scenarios()
    kpis = generate_apr_kpis()
    create_readme()

    print("\n" + "=" * 80)
    print("✅ NYOS APR DATA GENERATION COMPLETE!")
    print("=" * 80)
    print(f"\n📁 Output Directory: {OUTPUT_DIR}")
    print(f"📊 Total Datasets: {len(summary)}")
    print(f"📝 Total Records: {summary['records'].sum():,}")
    print(f"💾 Total Size: {summary['size_mb'].sum():.2f} MB")
    print("\n🔍 Hidden Scenarios Documented: 7")
    print("📈 APR KPIs Generated: 6 years")
    print("\n🚀 Ready for NYOS APR Demo!")
