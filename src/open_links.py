import argparse
import pandas as pd
import webbrowser
import time
import sys

def open_links_from_csv(file_path):
    """
    Reads a CSV file, extracts URLs from a specified column, and opens them in a web browser.

    Args:
        file_path (str): The path to the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        sys.exit(1)

    if 'job_url' not in df.columns:
        print(f"Error: The required column 'job_url' was not found in '{file_path}'.")
        sys.exit(1)

    urls = df['job_url'].dropna().tolist()

    if not urls:
        print("No URLs found in the 'job_url' column.")
        return

    link_count = len(urls)
    print(f"Found {link_count} links.")

    if link_count > 20:
        proceed = input("Proceed? (y/n): ").lower()
        if proceed != 'y':
            print("Operation cancelled by user.")
            return

    print("Opening links...")
    for i, url in enumerate(urls, 1):
        print(f"({i}/{link_count}) Opening: {url}")
        webbrowser.open(url)
        time.sleep(0.85)

    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Open all URLs in the 'job_url' column of a CSV file."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="The path to the CSV file."
    )
    args = parser.parse_args()
    
    open_links_from_csv(args.file_path)
