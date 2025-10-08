
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from pathlib import Path

def generate_analytics(input_path: str):
    """
    Generates a summary CSV and a plots image from a job search results CSV.

    :param input_path: Path to the input CSV file.
    """
    input_p = Path(input_path)
    if not input_p.exists() or os.path.getsize(input_p) == 0:
        print(f"Analytics skipped: File '{input_path}' is empty or does not exist.")
        return

    df = pd.read_csv(input_p)
    if df.empty:
        print(f"Analytics skipped: File '{input_path}' is empty.")
        return

    # Generate summary CSV
    analytics_df = df.groupby(['SS', 'KW']).size().reset_index(name='count')
    analytics_output_path = input_p.parent / f"{input_p.stem}_analytics.csv"
    analytics_df.to_csv(analytics_output_path, index=False)
    print(f"Analytics summary saved to {analytics_output_path}")

    # Generate plots
    fig, axes = plt.subplots(2, 1, figsize=(12, 16))
    fig.suptitle('Job Search Analytics', fontsize=16)

    # Plot 1: Job Count by Search Setting (SS)
    ss_counts = df['SS'].value_counts()
    sns.barplot(x=ss_counts.index, y=ss_counts.values, ax=axes[0])
    axes[0].set_title('Total Jobs per Search Setting (SS)')
    axes[0].set_xlabel('Search Setting')
    axes[0].set_ylabel('Number of Jobs')
    axes[0].tick_params(axis='x', rotation=45)

    # Plot 2: Job Count by Keyword (KW) within each Search Setting (SS)
    kw_ss_counts = df.groupby(['SS', 'KW']).size().unstack(fill_value=0)
    kw_ss_counts.plot(kind='bar', stacked=False, ax=axes[1])
    axes[1].set_title('Job Breakdown by Keyword (KW) per Search Setting (SS)')
    axes[1].set_xlabel('Search Setting')
    axes[1].set_ylabel('Number of Jobs')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].legend(title='Keyword')

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plots_output_path = input_p.parent / f"{input_p.stem}_plots.png"
    plt.savefig(plots_output_path)
    print(f"Analytics plots saved to {plots_output_path}")
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/analytics.py <path_to_input_csv>")
        sys.exit(1)
    
    input_csv_path = sys.argv[1]
    generate_analytics(input_csv_path)
