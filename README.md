# Duka Sales Exploration and Agent Network Clean-Up

## Project Summary

This project contains two data analysis engagements completed using Python, pandas, NumPy and Excel.

The first engagement analyses Duka Electronics sales data for the first half of 2026. The analysis examines branch performance, product performance, weekday versus weekend sales, monthly revenue trends and Premium online orders from Nairobi and Mombasa.

The second engagement audits and cleans mobile-money agent transaction data. The cleaning process addresses duplicate transactions, inconsistent transaction types, missing or invalid amounts, inconsistent date formats, transaction outliers and transactions linked to unknown agents. The cleaned transactions are then merged with the agent register and summarised by county and week.

## Repository Contents

- `generate_data.py` - generates the Duka sales dataset and mobile-money agent datasets.
- `duka_sales_exploration.ipynb` - contains the Duka Electronics sales exploration.
- `cleaning_pipeline.py` - contains the reusable `clean_agent_data()` cleaning function.
- `agent_cleanup.ipynb` - contains the agent data-quality audit, cleaning, validation and reporting.
- `excel/duka_branch_summary.xlsx` - Excel analysis containing SUMIFS, XLOOKUP and a PivotTable.
- `outputs/premium_online_coast_capital.csv` - Premium online orders from Nairobi and Mombasa.
- `outputs/agent_transactions_clean.csv` - final cleaned agent transaction dataset.
- `requirements.txt` - required Python libraries.

## How to Regenerate the Raw Data

From the project folder, run:

```bash
python generate_data.py