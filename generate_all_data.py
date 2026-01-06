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



def create_directory_structure():
    """Create the organized directory structure."""
    print("\n Creating directory structure...")

    APR_DATA_DIR.mkdir(exist_ok=True)

    for theme in THEMES:
        theme_dir = APR_DATA_DIR / theme
        theme_dir.mkdir(exist_ok=True)
        print(f"    {theme}/")

    print("  Directory structure ready")


def run_generator(script_name: str) -> bool:
    """Run a single generator script."""
    script_path = SCRIPT_DIR / script_name

    if not script_path.exists():
        print(f"     Script not found: {script_name}")
        return False

    print(f"\n Running: {script_name}")
    print("-" * 50)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPT_DIR),
            capture_output=False,
            text=True,
        )

        if result.returncode == 0:
            print(f"    {script_name} completed successfully")
            return True
        else:
            print(f"    {script_name} failed with code {result.returncode}")
            return False

    except Exception as e:
        print(f"    Error running {script_name}: {e}")
        return False


def organize_files_by_theme():
    """Move generated files to their theme directories."""
    print("\n📦 Organizing files by theme...")

    moved_count = 0

    for theme, prefixes in THEMES.items():
        theme_dir = APR_DATA_DIR / theme

        for prefix in prefixes:
            for csv_file in APR_DATA_DIR.glob(f"{prefix}*.csv"):
                if csv_file.parent == APR_DATA_DIR:  
                    dest = theme_dir / csv_file.name
                    shutil.move(str(csv_file), str(dest))
                    moved_count += 1
                    print(f"   {csv_file.name} → {theme}/")

    summary_files = ["_apr_kpis.csv", "_data_index.csv", "_hidden_scenarios.csv"]
    for sf in summary_files:
        src = APR_DATA_DIR / sf
        if src.exists():
            print(f"    {sf} (summary - kept in root)")

    print(f"\n   ✓ Organized {moved_count} files into theme directories")



def main():
    """Main entry point."""

    create_directory_structure()

    print("\n Starting data generation...")
    success_count = 0

    for script in GENERATORS:
        if run_generator(script):
            success_count += 1

    print(f"\n Completed {success_count}/{len(GENERATORS)} generators")

    organize_files_by_theme()


    print("\n Data generation complete!")
    print(" Data available at:", APR_DATA_DIR)
    print("\n Next steps:")
    print("\n Import data using python3 import_all_data.py")
    print("Start the backend: cd backend && uvicorn app.main:app --reload")
    print("Start the frontend: cd frontend && npm run dev")


if __name__ == "__main__":
    main()
