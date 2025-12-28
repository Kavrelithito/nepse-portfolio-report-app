# NEPSE Portfolio Summary

Automated **NEPSE portfolio analysis and PDF report generation** using Python and GitHub Actions.

This project reads a **Trade log excel file**, **Price file**, and produces a **reproducible PDF portfolio report**.

👉 **This is test portfoli summary**

---

## ✨ What This Project Does

- 📥 read Trade log file that user supplied
- 📊 Read stock price donwloaded by user from the Nepse
- 🧮 Calculates portfolio, sector, and profit summaries
- 📈 Generates charts and tables
- 🧾 Exports a single **PDF report**
- 🤖 Runs automatically via **Streamlit APP.py**
- ▶️ Can also be run **locally**

---

## 📂 Repository Structure

```text
├── data
│   └── NEPSE_Kavrelibis_2026.xlsm  
    # Portfolio Excel (downloaded from MEGA)
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
Use input Excel .xlsm
        ↓
GitHub Actions ?
        ↓
data/NEPSE_Kavrelibis_2026.xlsm
        ↓
data/Daily NEPSE price CSVs 
        ↓
Portfolio parsing & calculations
        ↓
Charts and tables
        ↓
PDF report → output/



⚠️ Important

APP dont store any input or output files/results



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



Email or Teams notifications

👤 Author

Netra Timalsina
Hydropower & Data Engineer
Python • R • Automation • Portfolio Analytics
