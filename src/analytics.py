import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import shutil
import json
import re
from pathlib import Path
from wordcloud import WordCloud
from collections import Counter

# The new, updated list of stop words
STOPWORDS = set([
    'm', 'w', 'd', 'f', 'genders', 'engineer', 'und', 'als', 'in', 'zum', 'im', 
    'bereich', 'all', 'schwerpunkt', 'std', 'woche', 'der', 'die', 'das', 'mit', 
    'für', 'jobbird', 'and', 'with', 'of', 'hi'
])

def sanitize_filename(filename):
    """Removes characters that are invalid for filenames."""
    return re.sub(r'[\\/*?:\"<>|]', "", filename)

def get_word_frequencies(series):
    """Calculates word frequencies from a pandas Series."""
    text = ' '.join(series.dropna().astype(str).str.lower())
    words = re.findall(r"[\w'-]+", text)
    filtered_words = [word for word in words if word not in STOPWORDS]
    return Counter(filtered_words)

def generate_word_cloud_image(frequencies, title, output_path):
    """Generates and saves a word cloud image from a frequency map."""
    if not frequencies:
        print(f"Skipping empty word cloud for: {title}")
        return
    wordcloud = WordCloud(
        width=800, height=400, background_color='white'
    ).generate_from_frequencies(frequencies)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(title)
    plt.axis('off')
    plt.savefig(output_path)
    plt.close()

def generate_analytics(input_path: str):
    """
    Generates a summary CSV with word frequencies, a main plot with bar charts,
    and a directory of individual word clouds for each keyword.
    """
    input_p = Path(input_path)
    if not input_p.exists() or os.path.getsize(input_p) == 0:
        print(f"Analytics skipped: File '{input_path}' is empty or does not exist.")
        return

    df = pd.read_csv(input_p)
    if df.empty:
        print(f"Analytics skipped: File '{input_path}' is empty.")
        return

    # --- 1. Revert Main Plot to 2x1 Bar Charts ---
    fig, axes = plt.subplots(2, 1, figsize=(12, 16))
    fig.suptitle('Job Search Analytics', fontsize=16)

    ss_counts = df['SS'].value_counts()
    sns.barplot(x=ss_counts.index, y=ss_counts.values, ax=axes[0])
    axes[0].set_title('Total Jobs per Search Setting (SS)')
    axes[0].tick_params(axis='x', rotation=45)

    if 'KW' in df.columns:
        kw_ss_counts = df.groupby(['SS', 'KW']).size().unstack(fill_value=0)
        kw_ss_counts.plot(kind='bar', stacked=False, ax=axes[1])
        axes[1].set_title('Job Breakdown by Keyword (KW) per SS')
        axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plots_output_path = input_p.parent / f"{input_p.stem}_plots.png"
    plt.savefig(plots_output_path)
    print(f"Main analytics plots saved to {plots_output_path}")
    plt.close()

    # --- 2. Directory Management for Clouds ---
    clouds_dir = input_p.parent / 'clouds'
    if clouds_dir.exists():
        shutil.rmtree(clouds_dir)
    clouds_dir.mkdir()
    print(f"Created clean directory: {clouds_dir}")

    # --- 3. Generate Keyword-Specific Clouds and Frequency Data ---
    analytics_data = []
    keywords = df['KW'].unique()
    total_keywords = len(keywords)

    for i, kw in enumerate(keywords):
        print(f"Processing keyword '{kw}' ({i+1}/{total_keywords})...")
        kw_df = df[df['KW'] == kw]
        count = len(kw_df)

        # Calculate frequencies
        title_freq = get_word_frequencies(kw_df['title'])
        location_freq = get_word_frequencies(kw_df['location'])

        # Generate and save cloud images
        sanitized_kw = sanitize_filename(kw)
        title_cloud_path = clouds_dir / f"{sanitized_kw}_{count}_title.png"
        location_cloud_path = clouds_dir / f"{sanitized_kw}_{count}_location.png"
        
        generate_word_cloud_image(title_freq, f"Keyword: '{kw}' ({count} Jobs)", title_cloud_path)
        generate_word_cloud_image(location_freq, f"Keyword: '{kw}' ({count} Jobs)", location_cloud_path)

        # Store data for CSV
        analytics_data.append({
            'KW': kw,
            'count': count,
            'title_word_frequencies': json.dumps(dict(title_freq.most_common(50))),
            'location_word_frequencies': json.dumps(dict(location_freq.most_common(50)))
        })

    # --- 4. Generate Enhanced Summary CSV ---
    summary_df = df.groupby(['SS', 'KW']).size().reset_index(name='count')
    freq_df = pd.DataFrame(analytics_data)
    
    # Merge the two dataframes
    final_df = pd.merge(summary_df, freq_df.drop('count', axis=1), on='KW', how='left')

    analytics_output_path = input_p.parent / f"{input_p.stem}_analytics.csv"
    final_df.to_csv(analytics_output_path, index=False)
    print(f"Enhanced analytics summary saved to {analytics_output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/analytics.py <path_to_input_csv>")
        sys.exit(1)
    
    input_csv_path = sys.argv[1]
    generate_analytics(input_csv_path)
