#!/usr/bin/env python3
"""
NYOS APR - Master Data Generator
=================================
Single script to generate all pharmaceutical APR data organized by theme.

This creates a complete 6-year dataset (2020-2025) for Annual Product Review analysis.

Directory Structure:
    apr_data/
    ├── manufacturing/       # Batch production records
    ├── quality/            # QC lab results, stability data
    ├── compliance/         # CAPAs, complaints, deviations
    ├── materials/          # Raw materials, supplier data
    ├── equipment/          # Calibration, maintenance
    ├── environment/        # Environmental monitoring
    └── release/            # Batch release decisions

Author: NYOS APR Team
Date: January 2026
"""

import subprocess
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
APR_DATA_DIR = SCRIPT_DIR / "apr_data"

# Theme-based subdirectories
THEMES = {
    "manufacturing": ["manufacturing_extended"],
    "quality": ["qc_lab_extended", "stability_data"],
    "compliance": ["capa_records", "customer_complaints"],
    "materials": ["raw_materials", "supplier_performance"],
    "equipment": ["equipment_calibration", "preventive_maintenance"],
    "environment": ["environmental_monitoring"],
    "release": ["batch_release"],
}

# Generator scripts in order of execution (dependencies matter!)
GENERATORS = [
    "generate_comprehensive_apr_data.py",  # Manufacturing - must be first
    "generate_qc_data.py",  # QC data - depends on manufacturing
    "generate_stability_data.py",  # Stability
    "generate_environmental_data.py",  # Environmental
    "generate_complaints_data.py",  # Complaints - depends on manufacturing
    "generate_capa_data.py",  # CAPAs - depends on complaints
    "generate_raw_materials_data.py",  # Raw materials
    "generate_equipment_data.py",  # Equipment
    "generate_batch_release_data.py",  # Batch release - depends on manufacturing & QC
    "generate_master_summary.py",  # Summary and KPIs - depends on all
]


def print_header():
    """Print a nice header."""
    print("\n" + "=" * 70)
    print("🏭 NYOS APR - Master Data Generator")
    print("=" * 70)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Output: {APR_DATA_DIR}")
    print("=" * 70)


def create_directory_structure():
    """Create the organized directory structure."""
    print("\n📂 Creating directory structure...")

    # Create main data directory
    APR_DATA_DIR.mkdir(exist_ok=True)

    # Create theme subdirectories
    for theme in THEMES:
        theme_dir = APR_DATA_DIR / theme
        theme_dir.mkdir(exist_ok=True)
        print(f"   ✓ {theme}/")

    print("   ✓ Directory structure ready")


def run_generator(script_name: str) -> bool:
    """Run a single generator script."""
    script_path = SCRIPT_DIR / script_name

    if not script_path.exists():
        print(f"   ⚠️  Script not found: {script_name}")
        return False

    print(f"\n🔄 Running: {script_name}")
    print("-" * 50)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPT_DIR),
            capture_output=False,
            text=True,
        )

        if result.returncode == 0:
            print(f"   ✅ {script_name} completed successfully")
            return True
        else:
            print(f"   ❌ {script_name} failed with code {result.returncode}")
            return False

    except Exception as e:
        print(f"   ❌ Error running {script_name}: {e}")
        return False


def organize_files_by_theme():
    """Move generated files to their theme directories."""
    print("\n📦 Organizing files by theme...")

    moved_count = 0

    for theme, prefixes in THEMES.items():
        theme_dir = APR_DATA_DIR / theme

        for prefix in prefixes:
            # Find all files with this prefix in the main apr_data directory
            for csv_file in APR_DATA_DIR.glob(f"{prefix}*.csv"):
                if csv_file.parent == APR_DATA_DIR:  # Only move files from root
                    dest = theme_dir / csv_file.name
                    shutil.move(str(csv_file), str(dest))
                    moved_count += 1
                    print(f"   {csv_file.name} → {theme}/")

    # Move summary files to root (keep them visible)
    summary_files = ["_apr_kpis.csv", "_data_index.csv", "_hidden_scenarios.csv"]
    for sf in summary_files:
        src = APR_DATA_DIR / sf
        if src.exists():
            print(f"   📊 {sf} (summary - kept in root)")

    print(f"\n   ✓ Organized {moved_count} files into theme directories")


def print_summary():
    """Print a summary of generated data."""
    print("\n" + "=" * 70)
    print("📊 DATA GENERATION SUMMARY")
    print("=" * 70)

    total_files = 0
    total_size = 0

    for theme in THEMES:
        theme_dir = APR_DATA_DIR / theme
        if theme_dir.exists():
            files = list(theme_dir.glob("*.csv"))
            size = sum(f.stat().st_size for f in files)
            total_files += len(files)
            total_size += size
            print(f"   {theme.upper()}: {len(files)} files ({size/1024/1024:.1f} MB)")

    # Root files
    root_files = list(APR_DATA_DIR.glob("*.csv"))
    if root_files:
        size = sum(f.stat().st_size for f in root_files)
        total_size += size
        print(f"   SUMMARIES: {len(root_files)} files ({size/1024:.1f} KB)")
        total_files += len(root_files)

    print("-" * 50)
    print(f"   TOTAL: {total_files} files ({total_size/1024/1024:.1f} MB)")
    print("=" * 70)


def create_readme():
    """Create a README file in the data directory."""
    readme_content = f"""# NYOS APR Data
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Directory Structure

```
apr_data/
├── manufacturing/       # Batch production records (CPPs, yields, deviations)
├── quality/            # QC lab results, stability studies (CQAs)
├── compliance/         # CAPAs, customer complaints, investigations
├── materials/          # Raw materials, supplier performance
├── equipment/          # Calibration records, preventive maintenance
├── environment/        # Environmental monitoring (temperature, particles)
├── release/            # Batch release decisions, QP reviews
└── _*.csv              # Summary files and KPIs
```

## Data Files

### Manufacturing
- `manufacturing_extended_YYYY.csv` - Yearly batch records
- `manufacturing_extended_ALL.csv` - Combined 6-year data

### Quality  
- `qc_lab_extended_YYYY.csv` - QC test results
- `stability_data_YYYY.csv` - Stability studies (ICH compliant)

### Compliance
- `capa_records_YYYY.csv` - Corrective/Preventive actions
- `customer_complaints_YYYY.csv` - Market complaints

### Materials
- `raw_materials_YYYY.csv` - Material receipts and testing
- `supplier_performance_YYYY.csv` - Supplier quality metrics

### Equipment
- `equipment_calibration_YYYY.csv` - Calibration records
- `preventive_maintenance_YYYY.csv` - Maintenance schedules

### Environment
- `environmental_monitoring_YYYY.csv` - Room monitoring data

### Release
- `batch_release_YYYY.csv` - QP release decisions

## Hidden Scenarios

The data includes realistic drift scenarios for AI detection:
- Equipment drift (Press-A hardness increasing)
- Seasonal variations
- Supplier quality issues
- Operator-related variations

See `_hidden_scenarios.csv` for the complete list.

## Usage

Import files through the NYOS web interface:
1. Go to "Import Data" tab
2. Select the appropriate data type
3. Upload the `*_ALL.csv` file for that type

## Product

Paracetamol 500mg Film-Coated Tablets
- Batch size: 200 kg
- Tablet weight: 600 mg
- Hardness target: 90 N
- Period: 2020-2025 (6 years)
"""

    readme_path = APR_DATA_DIR / "README.md"
    readme_path.write_text(readme_content)
    print(f"\n📝 Created README.md")


def main():
    """Main entry point."""
    print_header()

    # Step 1: Create directory structure
    create_directory_structure()

    # Step 2: Run all generators
    print("\n🚀 Starting data generation...")
    success_count = 0

    for script in GENERATORS:
        if run_generator(script):
            success_count += 1

    print(f"\n✅ Completed {success_count}/{len(GENERATORS)} generators")

    # Step 3: Organize files by theme
    organize_files_by_theme()

    # Step 4: Create documentation
    create_readme()

    # Step 5: Print summary
    print_summary()

    print("\n🎉 Data generation complete!")
    print("📁 Data available at:", APR_DATA_DIR)
    print("\n💡 Next steps:")
    print("   1. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Import data via the web interface")
    print()


if __name__ == "__main__":
    main()
