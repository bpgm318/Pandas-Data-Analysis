# Telecom Usage Analysis with Pandas

A Python project that explores mobile data and voice usage for **2,808 users** over **April 2025 to March 2026**. It uses pandas to clean and summarize the data and Matplotlib to generate charts.

The analysis identifies monthly usage patterns, high-usage users, differences in usage between users, and changes in each user's usage over time.

## Datasets

| File | Description | Unit |
| --- | --- | --- |
| `mb.csv` | Monthly mobile data usage | Megabytes (MB) |
| `minutes.csv` | Monthly mobile voice usage | Minutes |

Each dataset contains one row per user and twelve monthly usage columns. The script renames invoice-number headings to their corresponding months and replaces missing usage values with zero.

## Repository Structure

```text
Pandas-Data-Analysis/
├── README.md
└── TelecomPandasAnalysis/
    ├── main.py
    ├── analysis.py
    ├── mb.csv
    ├── minutes.csv
    └── results/              # Created when the script runs
```

- **`main.py`** starts the program.
- **`analysis.py`** loads the datasets, calculates statistics, prints reports, and saves CSVs and charts.
- **`results/`** contains generated outputs and does not need to be uploaded to run the project.

## Setup and Usage

Install Python 3 and the two libraries used directly by the script:

```bash
python -m pip install pandas matplotlib
```

Download and extract this repository, or clone it:

```bash
git clone https://github.com/bpgm318/Pandas-Data-Analysis.git
cd Pandas-Data-Analysis
```

From the repository's root folder, run:

```bash
python TelecomPandasAnalysis/main.py
```

Alternatively, open `main.py` in your Python editor and run it there.

Keep `main.py`, `analysis.py`, `mb.csv`, and `minutes.csv` together in the same folder. The script locates its input files relative to `analysis.py` and automatically creates a `results` folder beside it.

The simplified version uses fixed settings: it prints reports and saves all CSVs and charts without opening chart windows. It has no command-line options or input prompts. Repeated runs overwrite output files with the same names.

## Analysis

### Per-User Statistics

For both data and voice usage, the script calculates:

- Average monthly usage over twelve months
- Highest monthly usage and the month it occurred
- Standard deviation of usage across the twelve months
- Total annual usage
- Percentage share of overall usage
- Low, medium, or high usage category

### Monthly Statistics

For each month, the script calculates total usage, average usage per user, standard deviation between users, maximum individual usage, and the user responsible for that maximum.

### Printed Reports

The terminal displays these reports for each dataset:

- Top user for each month
- Top ten users by average usage
- Top ten users by standard deviation
- Top twenty users by percentage share of usage
- Users averaging more than **51,200 MB** or **2,000 minutes** per month
- Number of users in each usage category

## Usage Categories

Categories are based on the user's average monthly usage across all twelve months.

| Category | Data Usage (MB) | Voice Usage (Minutes) |
| --- | --- | --- |
| Low Usage | Up to 3,000 | Up to 500 |
| Medium Usage | More than 3,000 and up to 30,000 | More than 500 and up to 1,600 |
| High Usage | More than 30,000 | More than 1,600 |

Averages retain decimal precision when assigning categories.

## Generated Files

### CSV Reports

Seven CSV files are saved in `TelecomPandasAnalysis/results/`:

| File | Contents |
| --- | --- |
| `Takeaway (mb).csv` | Per-user data-usage statistics and categories |
| `Takeaway (minutes).csv` | Per-user voice-usage statistics and categories |
| `monthly_mb.csv` | Monthly data-usage statistics |
| `monthly_minutes.csv` | Monthly voice-usage statistics |
| `top_monthly_users_mb.csv` | Highest data-usage user and amount for each month |
| `top_monthly_users_minutes.csv` | Highest voice-usage user and amount for each month |
| `combined_averages.csv` | Data and voice averages joined by user identifier |

### Charts

Six PNG charts are generated for each dataset, giving **twelve charts** in total:

| Filename Pattern | Chart |
| --- | --- |
| `monthly_total_<unit>.png` | Total usage by month |
| `monthly_average_<unit>.png` | Average usage per user by month |
| `monthly_std_<unit>.png` | Standard deviation between users by month |
| `monthly_maximum_<unit>.png` | Maximum individual usage by month |
| `highest_month_<unit>.png` | Number of users whose highest usage occurred in each month |
| `usage_type_<unit>.png` | Number of users in each usage category |

`<unit>` is replaced with `mb` or `minutes`, for example `monthly_total_mb.png`.

## Calculation Notes

- Missing usage is treated as **zero**, and monthly averages always divide by twelve. This assumes blanks mean no usage rather than unavailable measurements.
- Standard deviations use the sample definition (`ddof=1`).
- If multiple months tie for a user's maximum, the earliest month is selected. Users with zero usage throughout the year have no highest month and are excluded from the highest-month chart.
- If users tie for a monthly maximum, the first user in the source table is selected.
- `Proportion` is expressed as a percentage: a value of `25` means 25% of that dataset's total usage.
- The combined averages report uses an inner join on `USER`, so it includes identifiers present in both datasets.
- This simplified script assumes the supplied CSV structure, valid numeric usage, unique user identifiers, and a positive overall usage total for each dataset. It does not include custom input validation.

## Python Concepts Used

- pandas DataFrames and CSV input/output
- Column renaming and missing-value handling
- Row and column aggregations
- Filtering, ranking, and category assignment
- Joining tables by user identifier
- Functions, dictionaries, and loops
- Matplotlib bar charts
- File paths with `pathlib`
