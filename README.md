# NYOS ARP

Our web app is a full-stack Pharmaceutical Quality Intelligence platform designed for Annual Product Review (APR) analysis. It features an advanced analytics dashboard, a synthetic data generation suite, and an AI assistant powered by Google Gemini to analyze manufacturing data, detect trends, and generate reports.

The application allows users to generate a comprehensive synthetic dataset for, import data into the app, and then use a web interface to visualize, analyze, and query the data with natural language in our AI chat bot.

## Key Features

- **Full-Stack Application**: Modern web application built with a React frontend and a FastAPI Python backend.
- **Advanced Analytics Dashboard**: Interactive charts and KPIs for monitoring production, quality, and compliance metrics.
- **AI Assistant**: A chat interface powered by Google Gemini to query data in a chat. Can also generate executive summaries, and create full APR reports.
- **Synthetic Data Generation**: A suite of Python scripts to create realistic (fictive) pharmaceutical data (Manufacturing, QC, Stability, Complaints, CAPA, etc.) for 2020-2025. (Used to test our model)
- **Embedded Scenarios**: The dataset includes hidden scenarios like equipment degradation, supplier quality issues, and seasonal effects for testing AI detection capabilities.
- **Trend & Anomaly Detection**: Endpoints and UI components for analyzing parameter drifts, detecting anomalies, and comparing performance over different periods.
- **Data Import System**: A simple interface and script to upload the generated CSV files into the application's database.

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Google Generative AI  (classic backend, efficient)
- **Frontend**: React, Vite, Tailwind CSS (modern and complete)
- **Data Generation**: Python, Pandas, Faker (complete dataset)
- **Database**: SQLite (simple/fast to use and setup)

## Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- Python 3.8+
- Node.js and npm
- A Google Gemini API Key to put in a .env file

### 2. Generate Synthetic Data

This step creates a comprehensive dataset in the `apr_data/` directory, organized in different theme.

```bash
python3 generate_all_data.py
```

### 3. Backend Setup

Set up and run the FastAPI server.

```bash
# First of all, create and activate a virtual environment
#At root of the project:
python3 -m venv env
source env/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Remember to create a .env file with your API key and the database URL: 
DATABASE_URL=sqlite:///./nyos.db

# When dependencies are installed: 
#Run the backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Import Data (for testing so you don't need to add each file by hand in the app)

With the backend server running, open a **new terminal window** in the project's root directory and run the import script. This will fill the database with the data generated in step 3.

```bash
python3 import_all_data.py
```

### 5. Frontend Setup

Set up and run the React development server.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the frontend server
npm run dev
```

### 6. Access the Application

The NYOS application is now running. Open your browser and navigate to:
**[http://localhost:5173](http://localhost:5173)**

## Project Structure

```
.
├── backend/                # FastAPI application
│   ├── app/                # Main application source code
│   │   ├── services/       # Contains gemini_service.py
│   │   ├── routers/        # API endpoints (analytics, chat, data)
│   │   ├── models.py       # SQLAlchemy database models
│   │   └── main.py         # FastAPI app entry point
│   └── requirements.txt
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components (Dashboard, Chat, etc.)
│   │   ├── App.jsx         # Main application component
│   │   └── api.js          # API client for backend communication
│   └── vite.config.js
├── generate_all_data.py    # Master script to generate all datasets
├── import_all_data.py      # Script to import generated data into the DB
└── ... (all other data generation scripts)
```

## Dataset Overview

The project includes a powerful data generation engine that creates a realistic APR dataset for "Paracetamol 500mg Tablets" from 2020 to 2025.

**Data Categories Generated:**
-   **Manufacturing**: Batch production records with Critical Process Parameters (CPPs).
-   **Quality Control**: Lab results for Critical Quality Attributes (CQAs), including assay, dissolution, impurities, etc.
-   **Stability**: Long-term, accelerated, and intermediate stability studies.
-   **Compliance**: CAPA records, customer complaints, and deviations.
-   **Materials**: Raw material receipts and supplier performance data.
-   **Equipment**: Calibration and preventive maintenance logs.
-   **Environment**: Clean room environmental monitoring data.
-   **Release**: Batch release decisions and disposition records.
