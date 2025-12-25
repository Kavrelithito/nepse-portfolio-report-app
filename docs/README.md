# NEPSE Portfolio Summary

Automated **NEPSE portfolio analysis and PDF report generation** using Python and GitHub Actions.

This project reads a **private macro-enabled Excel portfolio (`.xlsm`) stored on MEGA**, combines it with daily NEPSE market prices, and produces a **reproducible PDF portfolio report**.

👉 **Private financial data is never committed to GitHub.**

---

## ✨ What This Project Does

- 📥 Downloads portfolio Excel (`.xlsm`) securely from **MEGA**
- 📊 Downloads daily NEPSE prices from GitHub
- 🧮 Calculates portfolio, sector, and profit summaries
- 📈 Generates charts and tables
- 🧾 Exports a single **PDF report**
- 🤖 Runs automatically via **GitHub Actions**
- ▶️ Can also be run **locally**

---

## 📂 Repository Structure

```text
├── data
│   └── NEPSE_Kavrelibis_2025.xlsm      # Portfolio Excel (downloaded from MEGA)
├── docs
│   ├── DECISIONS.md                   # Architecture & design decisions
│   ├── README.md                     # This documentation
│   ├── STATUS.md                     # Current project status
│   └── TODO.md                       # Planned improvements
├── output
│   └── nepse_portfolio_report_latest.pdf
├── src
│   └── nepse_portfoli
│       ├── app
│       │   └── make_report_pdf.py     # Main entry point
│       ├── core
│       │   └── summary_pi.py          # Business logic & plotting
│       └── io
│           ├── git_hub_price_download.py
│           └── portfolio_io.py
├── PROJECT_STRUCTURE.txt
├── update_structure.sh
└── .gitignore

🔁 Data Flow
MEGA (Excel .xlsm)
        ↓
GitHub Actions (megadl)
        ↓
data/NEPSE_Kavrelibis_2025.xlsm
        ↓
Daily NEPSE price CSVs (GitHub)
        ↓
Portfolio parsing & calculations
        ↓
Charts and tables
        ↓
PDF report → output/

📥 Excel Input Source (MEGA)

⚠️ Important

The portfolio Excel file is NOT stored in this repository.

It is downloaded dynamically from MEGA every time the workflow runs.

Excel Details

Storage: MEGA.nz

File name: NEPSE_Kavrelibis_2025.xlsm

Format: .xlsm (macros are ignored by Python)

Download tool: megatools (megadl)

Reason for using MEGA:

Protect private financial data

Avoid committing large binary files

Allow Excel updates without changing code

🔐 Required GitHub Secret

The following secret must be configured in the repository:

Secret name	Description
MEGA_XLSM_URL	MEGA download link for the Excel portfolio file

If this secret is missing or invalid, the workflow will fail.

📍 Expected Excel Location

After download, the Excel file must exist at:

data/NEPSE_Kavrelibis_2025.xlsm


This path is explicitly used by:

src/nepse_portfoli/app/make_report_pdf.py

⚙️ GitHub Actions Workflow

Workflow name: Run NEPSE Portfolio Summary

Triggers

Manual trigger (workflow_dispatch)

Push to main

Workflow Steps

Checkout repository

Setup Python 3.12

Install megatools

Download Excel from MEGA

Install Python dependencies

Run PDF generation script

Upload PDF as workflow artifact

Excel Download Step (Excerpt)
- name: Download Excel from MEGA into data/
  env:
    MEGA_XLSM_URL: ${{ secrets.MEGA_XLSM_URL }}
  run: |
    mkdir -p data
    megadl "$MEGA_XLSM_URL" --path "data/NEPSE_Kavrelibis_2025.xlsm"

▶️ Running Locally
1️⃣ Create Virtual Environment
cd Nepse_portfolio_summary_pr

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pandas matplotlib openpyxl requests

2️⃣ Provide Excel File

For local execution, manually place the Excel file at:

data/NEPSE_Kavrelibis_2025.xlsm


(Or implement MEGA download locally if desired.)

3️⃣ Run the Script
export PYTHONPATH=src          # Windows: set PYTHONPATH=src
python src/nepse_portfoli/app/make_report_pdf.py

📄 Output
output/nepse_portfolio_report_latest.pdf


The PDF includes:

Portfolio overview

Sector allocation

Realized profit summary

Charts and tables

🧠 Architecture Principles

Clear separation of concerns:

IO layer

Core business logic

Application layer

CI-first design

Deterministic and reproducible outputs

No private data in Git

Minimal dependencies

🛠 Planned Improvements

See docs/TODO.md, including:

Streamlit dashboard

Multi-portfolio support

Scheduled daily execution

Upload PDF to OneDrive / SharePoint

Email or Teams notifications

👤 Author

Netra Timalsina
Hydropower & Data Engineer
Python • R • Automation • Portfolio Analytics
