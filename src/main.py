import argparse
from src.agents.fisher import Agent_Fisher
from src.agents.perry import Agent_Perry
from src.utils.config import get_user_configs, get_proxy

def main():
    """
    JobSpy CLI tool to scrape job postings.

    0. install poetry: curl -sSL https://install.python-poetry.org | python3 -
    1. install dependencies: poetry install
    
    
    This script runs the JobSpy scrapers based on user configurations.
    It fetches job data, aggregates it, and saves the results.

    Usage:
        poetry run python -m src.main [config_path]

    Arguments:
        config_path (optional): Path to a specific user YAML configuration file.
                                If not provided, the script will run for all user
                                configurations found in the 'src/users' directory.

    Example:
        # Run for all users
        poetry run python -m src.main

        # Run for a specific user configuration
        poetry run python -m src.main src/users/default/default_config.yaml

        # Open links from a CSV file
        poetry run python -m src.open_links src/output/default/20251007/lux_std.csv
    """
    parser = argparse.ArgumentParser(description="JobSpy CLI")
    parser.add_argument('config_path', nargs='?', default=None, help="Path to a specific user config file.")
    args = parser.parse_args()

    user_configs = get_user_configs(args.config_path)
    proxy = get_proxy()

    fisher = Agent_Fisher(proxy)
    for user_config in user_configs:
        fisher.run_user(user_config)

    perry = Agent_Perry(user_configs)
    perry.daily_aggregate()
    perry.agg_the_agg()

if __name__ == "__main__":
    main()
