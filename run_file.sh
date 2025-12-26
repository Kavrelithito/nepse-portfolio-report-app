#!/bin/bash
set -e

# Go to folder where script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Make src importable
export PYTHONPATH="$SCRIPT_DIR/src"

# Run Streamlit app
streamlit run app.py
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .venv/bin/activate
PYTHONPATH=src python src/nepse_portfoli/app/make_report_pdf.py

