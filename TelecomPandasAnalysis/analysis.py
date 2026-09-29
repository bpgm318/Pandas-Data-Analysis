"""Reusable analysis of April 2025–March 2026 telecom usage."""

import argparse
from pathlib import Path

import numpy as np
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


def load_usage(path, unit):
    """Validate measurements and IDs, then fill missing usage with zero."""
    if unit not in THRESHOLDS:
        raise ValueError(f'Unsupported unit: {unit}')
    frame = pd.read_csv(path, dtype={'Unnamed: 0': 'string', 'USER': 'string'})
    frame = frame.rename(columns={
        'Unnamed: 0': 'USER', **dict(zip(INVOICES, month_columns(unit)[1:]))
    })
    expected = ['USER', *month_columns(unit)]
    if not frame.columns.is_unique or set(frame.columns) != set(expected):
        raise ValueError(f'{path}: expected USER and exactly twelve monthly columns')
    frame = frame.loc[:, expected].copy()
    if frame.empty:
        raise ValueError(f'{path}: no users found')
    if frame['USER'].isna().any() or frame['USER'].str.strip().eq('').any():
        raise ValueError(f'{path}: missing user identifiers')
    if frame['USER'].duplicated().any():
        raise ValueError(f'{path}: duplicate user identifiers')
    columns = month_columns(unit)
    values = frame[columns].apply(pd.to_numeric, errors='raise').fillna(0)
    if not np.isfinite(values.to_numpy(dtype=float)).all() or values.lt(0).any().any():
        raise ValueError(f'{path}: usage must be finite and nonnegative')
    frame[columns] = values
    return frame


def analyze_usage(frame, unit):
    """Use monthly columns only; preserve precision and source order for ties."""
    values = frame[month_columns(unit)]
    averages = values.mean(axis=1)
    totals = values.sum(axis=1)
    maximum = values.max(axis=1)
    grand_total = totals.sum()
    low, high = THRESHOLDS[unit]
    summary = pd.DataFrame({
        'USER': frame['USER'],
        f'12 Month Average ({unit})': averages,
        f'12 Month Max ({unit})': maximum,
        'Highest Month': values.idxmax(axis=1).where(maximum.gt(0)),
        'User std': values.std(axis=1),
        'Total': totals,
        'Proportion': totals.div(grand_total).mul(100) if grand_total else 0.0,
        'Type': np.select([averages.gt(high), averages.gt(low)],
                          ['High Usage', 'Medium Usage'], default='Low Usage'),
    })
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
    return summary, monthly, top_users


def save_charts(summary, monthly, unit, output_dir, show=False):
    """Save plots with separate axes for each unit; display only on request."""
    import matplotlib

    if not show:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    series = {
        'monthly_total': (monthly.set_index('Month')['Total'], 'Total usage', unit),
        'monthly_average': (monthly.set_index('Month')['Average'], 'Average per user', unit),
        'monthly_std': (monthly.set_index('Month')['Std'], 'Sample standard deviation', unit),
        'monthly_maximum': (monthly.set_index('Month')['Maximum'], 'Maximum per month', unit),
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
        if show:
            plt.show()
        plt.close(fig)


def run_analysis(data_dir, output_dir, plots=True, show=False):
    """Require matching user sets before writing summaries and charts."""
    frames = {unit: load_usage(data_dir / f'{unit}.csv', unit) for unit in THRESHOLDS}
    if set(frames['mb']['USER']) != set(frames['minutes']['USER']):
        raise ValueError('Data and voice user sets differ; reconcile before combining')
    results = {unit: analyze_usage(frame, unit) for unit, frame in frames.items()}
    output_dir.mkdir(parents=True, exist_ok=True)
    for unit, (summary, monthly, top_users) in results.items():
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
        if plots:
            save_charts(summary, monthly, unit, output_dir, show)
    combined = results['mb'][0][['USER', '12 Month Average (mb)']].merge(
        results['minutes'][0][['USER', '12 Month Average (minutes)']],
        on='USER', validate='one_to_one',
    )
    combined.to_csv(output_dir / 'combined_averages.csv', index=False)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=BASE_DIR)
    parser.add_argument('--output-dir', type=Path, default=BASE_DIR / 'results')
    parser.add_argument('--no-plots', action='store_true', help='Export tables only')
    parser.add_argument('--show', action='store_true', help='Also display charts')
    args = parser.parse_args()
    if args.no_plots and args.show:
        parser.error('--show and --no-plots cannot be combined')
    run_analysis(args.data_dir, args.output_dir, not args.no_plots, args.show)
