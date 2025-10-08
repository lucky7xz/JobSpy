import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
from pathlib import Path
from wordcloud import WordCloud

def generate_analytics(input_path: str):
    """
    Generates a summary CSV and a 2x2 plots image (bar charts and word clouds)
    from a job search results CSV.

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

    # --- 1. Generate Summary CSV ---
    analytics_df = df.groupby(['SS', 'KW']).size().reset_index(name='count')
    analytics_output_path = input_p.parent / f"{input_p.stem}_analytics.csv"
    analytics_df.to_csv(analytics_output_path, index=False)
    print(f"Analytics summary saved to {analytics_output_path}")

    # --- 2. Generate 2x2 Plots Image ---
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Job Search Analytics', fontsize=20)

    # Plot 1: Job Count by Search Setting (SS)
    ss_counts = df['SS'].value_counts()
    sns.barplot(x=ss_counts.index, y=ss_counts.values, ax=axes[0, 0])
    axes[0, 0].set_title('Total Jobs per Search Setting (SS)')
    axes[0, 0].set_xlabel('Search Setting')
    axes[0, 0].set_ylabel('Number of Jobs')
    axes[0, 0].tick_params(axis='x', rotation=45)

    # Plot 2: Job Count by Keyword (KW) within each Search Setting (SS)
    if 'KW' in df.columns:
        kw_ss_counts = df.groupby(['SS', 'KW']).size().unstack(fill_value=0)
        kw_ss_counts.plot(kind='bar', stacked=False, ax=axes[0, 1])
        axes[0, 1].set_title('Job Breakdown by Keyword (KW) per SS')
        axes[0, 1].set_xlabel('Search Setting')
        axes[0, 1].set_ylabel('Number of Jobs')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].legend(title='Keyword')

    # Helper for word clouds
    def generate_wordcloud(series, ax, title):
        text = ' '.join(series.dropna().astype(str).str.lower())
        if not text:
            ax.text(0.5, 0.5, 'No Data', horizontalalignment='center', verticalalignment='center')
            ax.set_title(title)
            ax.axis('off')
            return
        # Regex to keep hyphenated words as one token
        stopwords = set(['m', 'w', 'd','f' 'genders', 'engineer', 'und', 'als', 'in', 'zum', 'im', 'bereich','all', 'schwerpunkt', 'std', 'woche','der','die','das','mit','für','mit','jobbird','and','with','of','genders','hi',])
        wordcloud = WordCloud(
            width=800, height=400, background_color='white',
            stopwords=stopwords,
            regexp=r"[\w'-]+"
        ).generate(text)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.set_title(title)
        ax.axis('off')

    # Plot 3: Location Word Cloud
    generate_wordcloud(df['location'], axes[1, 0], 'Location Word Cloud')

    # Plot 4: Job Title Word Cloud
    generate_wordcloud(df['title'], axes[1, 1], 'Job Title Word Cloud')

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