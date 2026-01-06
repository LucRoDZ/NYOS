#!/usr/bin/env python3
"""
NYOS - Automatic Data Importer
Imports all generated CSV data year by year into the database
"""

import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
APR_DATA_DIR = Path(__file__).parent / "apr_data"

# Define all data files to import with their types
DATA_FILES = {
    "manufacturing": {
        "folder": "manufacturing",
        "pattern": "manufacturing_extended_{year}.csv",
        "type": "batch",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "quality_control": {
        "folder": "quality",
        "pattern": "qc_lab_extended_{year}.csv",
        "type": "qc",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "complaints": {
        "folder": "compliance",
        "pattern": "customer_complaints_{year}.csv",
        "type": "complaint",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "capa": {
        "folder": "compliance",
        "pattern": "capa_records_{year}.csv",
        "type": "capa",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "equipment": {
        "folder": "equipment",
        "pattern": "equipment_calibration_{year}.csv",
        "type": "equipment",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "environmental": {
        "folder": "environment",
        "pattern": "environmental_monitoring_{year}.csv",
        "type": "environmental",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "stability": {
        "folder": "quality",
        "pattern": "stability_data_{year}.csv",
        "type": "stability",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "raw_materials": {
        "folder": "materials",
        "pattern": "raw_materials_{year}.csv",
        "type": "raw_material",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
    "batch_release": {
        "folder": "release",
        "pattern": "batch_release_{year}.csv",
        "type": "batch_release",
        "years": [2020, 2021, 2022, 2023, 2024, 2025],
    },
}


def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/data/dashboard", timeout=5)
        return response.status_code == 200
    except:
        return False


def import_file(filepath: Path, data_type: str) -> dict:
    """Import a single CSV file"""
    if not filepath.exists():
        return {"success": False, "error": f"File not found: {filepath}"}

    try:
        with open(filepath, "rb") as f:
            files = {"file": (filepath.name, f, "text/csv")}
            response = requests.post(
                f"{BASE_URL}/data/upload",
                files=files,
                params={"data_type": data_type},
                timeout=300,  # 5 minutes timeout for large files
            )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("=" * 60)
    print("🏭 NYOS - Automatic Data Importer")
    print("=" * 60)

    # Check backend
    print("\n📡 Checking backend connection...")
    if not check_backend():
        print("❌ Backend not responding at", BASE_URL)
        print(
            "   Please start the backend first: cd backend && uvicorn app.main:app --reload"
        )
        return
    print("✅ Backend is running")

    # Check data directory
    print(f"\n📁 Data directory: {APR_DATA_DIR}")
    if not APR_DATA_DIR.exists():
        print("❌ Data directory not found!")
        return

    total_imported = 0
    total_errors = 0

    # Import each data type
    for name, config in DATA_FILES.items():
        print(f"\n{'─' * 50}")
        print(f"📊 Importing {name.upper()}")
        print(f"{'─' * 50}")

        folder_path = APR_DATA_DIR / config["folder"]
        if not folder_path.exists():
            print(f"   ⚠️  Folder not found: {folder_path}")
            continue

        for year in config["years"]:
            filename = config["pattern"].format(year=year)
            filepath = folder_path / filename

            if not filepath.exists():
                print(f"   ⚠️  {year}: File not found - {filename}")
                continue

            print(f"   📥 {year}: Importing {filename}...", end=" ", flush=True)
            result = import_file(filepath, config["type"])

            if result["success"]:
                count = result["data"].get("count", "?")
                print(f"✅ {count} records")
                total_imported += count if isinstance(count, int) else 0
            else:
                print(f"❌ Error: {result['error'][:50]}...")
                total_errors += 1

    # Summary
    print("\n" + "=" * 60)
    print("📋 IMPORT SUMMARY")
    print("=" * 60)
    print(f"   ✅ Total records imported: {total_imported:,}")
    print(f"   ❌ Errors: {total_errors}")

    # Verify data
    print("\n📊 Verifying imported data...")
    try:
        response = requests.get(f"{BASE_URL}/data/dashboard")
        if response.status_code == 200:
            data = response.json()
            print(f"   📦 Total batches: {data.get('total_batches', 0):,}")
            print(f"   📈 Average yield: {data.get('avg_yield', 0):.2f}%")
            print(f"   📞 Open complaints: {data.get('complaints_open', 0)}")
            print(f"   🔧 Open CAPAs: {data.get('capas_open', 0)}")
    except Exception as e:
        print(f"   ⚠️  Could not verify: {e}")

    print("\n✨ Import complete! You can now use the NYOS dashboard.")
    print("   Frontend: http://localhost:5173")


if __name__ == "__main__":
    main()
