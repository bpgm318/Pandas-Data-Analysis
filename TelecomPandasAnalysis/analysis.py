"""Analysis of April 2025 to March 2026 telecom usage."""

from pathlib import Path

import pandas as pd

MONTHS = ('Apr-25', 'May-25', 'Jun-25', 'Jul-25', 'Aug-25', 'Sep-25',
          'Oct-25', 'Nov-25', 'Dec-25', 'Jan-26', 'Feb-26', 'Mar-26')
INVOICES = ('2991603593', '3005992431', '3019858340', '3037885950',
            '3051482952', '3073819737', '3088209048', '3102831898',
            '3117565686', '3132275148', '3146908306')
THRESHOLDS = {'mb': (3000, 30000), 'minutes': (500, 1600)}
BASE_DIR = Path(__file__).resolve().parent


def month_columns(unit):
    return [f'{month} ({unit})' for month in MONTHS]


def save_charts(summary, monthly, unit, output_dir):
    """Save six charts as PNG files."""
    import matplotlib

    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    by_month = monthly.set_index('Month')
    series = {
        'monthly_total': (by_month['Total'], 'Total usage', unit),
        'monthly_average': (by_month['Average'], 'Average per user', unit),
        'monthly_std': (by_month['Std'], 'Sample standard deviation', unit),
        'monthly_maximum': (by_month['Maximum'], 'Maximum per month', unit),
        'highest_month': (
            summary['Highest Month'].value_counts().reindex(month_columns(unit), fill_value=0),
            'Highest month (positive-usage users)', 'Users'),
        'usage_type': (
            summary['Type'].value_counts().reindex(
                ['Low Usage', 'Medium Usage', 'High Usage'], fill_value=0),
            'Usage classification', 'Users'),
    }
    for name, (data, title, ylabel) in series.items():
        fig, ax = plt.subplots(figsize=(10, 5))
        data.plot.bar(ax=ax, title=f'{title} ({unit})', rot=45)
        ax.set_ylabel(ylabel)
        fig.tight_layout()
        fig.savefig(output_dir / f'{name}_{unit}.png', dpi=150)
        plt.close(fig)


def main():
    """Load, analyze, and report both datasets using fixed settings."""
    output_dir = BASE_DIR / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    average_tables = []

    for unit, (low, high) in THRESHOLDS.items():
        frame = pd.read_csv(BASE_DIR / f'{unit}.csv', dtype={'Unnamed: 0': 'string', 'USER': 'string'})
        frame = frame.rename(columns={
            'Unnamed: 0': 'USER', **dict(zip(INVOICES, month_columns(unit)[1:]))
        })
        columns = month_columns(unit)
        frame[columns] = frame[columns].fillna(0)

        values = frame[columns]
        averages = values.mean(axis=1)
        totals = values.sum(axis=1)
        maximum = values.max(axis=1)
        grand_total = totals.sum()
        summary = pd.DataFrame({
            'USER': frame['USER'],
            f'12 Month Average ({unit})': averages,
            f'12 Month Max ({unit})': maximum,
            'Highest Month': values.idxmax(axis=1).where(maximum.gt(0)),
            'User std': values.std(axis=1),
            'Total': totals,
            'Proportion': totals.div(grand_total).mul(100),
            'Type': 'Low Usage',
        })
        summary.loc[averages > low, 'Type'] = 'Medium Usage'
        summary.loc[averages > high, 'Type'] = 'High Usage'
        monthly = pd.DataFrame({
            'Month': MONTHS,
            'Total': values.sum().to_numpy(),
            'Average': values.mean().to_numpy(),
            'Std': values.std().to_numpy(),
            'Maximum': values.max().to_numpy(),
        })
        top_users = pd.DataFrame({
            'Month': MONTHS,
            'USER': frame.loc[values.idxmax().to_numpy(), 'USER'].to_numpy(),
            'Amount': values.max().to_numpy(),
        })

        summary.to_csv(output_dir / f'Takeaway ({unit}).csv', index=False)
        monthly.to_csv(output_dir / f'monthly_{unit}.csv', index=False)
        top_users.to_csv(output_dir / f'top_monthly_users_{unit}.csv', index=False)
        average = f'12 Month Average ({unit})'
        for title, table in (
            ('Top monthly users', top_users),
            ('Top 10 averages', summary.nlargest(10, average)),
            ('Top 10 standard deviations', summary.nlargest(10, 'User std')),
            ('Top 20 usage shares', summary.nlargest(20, 'Proportion')),
            ('Users above threshold', summary.loc[
                summary[average].gt(51200 if unit == 'mb' else 2000)]),
        ):
            print(f'\n{title} ({unit})\n{table.to_string(index=False)}')
        print(f'\nUsage types ({unit})\n{summary["Type"].value_counts()}')
        save_charts(summary, monthly, unit, output_dir)
        average_tables.append(summary[['USER', average]])

    combined = average_tables[0].merge(average_tables[1], on='USER')
    combined.to_csv(output_dir / 'combined_averages.csv', index=False)
