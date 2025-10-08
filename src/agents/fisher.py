import os
import random
import csv
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
import glob

from src.utils.logger import get_logger

logger = get_logger(__name__)

class Agent_Fisher:
    def __init__(self, proxy):
        logger.info("Instantiating Fisher...")
        self.date_run = self.get_date()
        self.proxy = proxy
        logger.info(" / ***Agent Fisher is online *** /\n\n")

    @staticmethod
    def get_date() -> str:
        now = datetime.now()
        date = now.strftime("%Y%m%d")
        return date

    def update_keywords_left(self, kewords_for_this_search: list, ss_out_path: str) -> list[str]:
        files = glob.glob(os.path.join(ss_out_path, "*.csv"))
        files = [os.path.basename(file) for file in files]

        keywords_done = [keyword for keyword in kewords_for_this_search if f"{keyword}.csv" in files]
        keywords_left = [keyword for keyword in kewords_for_this_search if keyword not in keywords_done]

        logger.info(f"--- Path: {ss_out_path}/*.csv ---")
        logger.info(f"Keywords done:  {len(keywords_done)} : \n {keywords_done} \n" )
        logger.info(f"Keywords left: {len(keywords_left)} : \n {keywords_left} \n")
        return keywords_left

    def run_search_setting(self, username: str, search_setting: dict, date: str) -> bool:
        empty_jobs = pd.DataFrame(columns=["job_url",
        "site", "title", "company", "company_url", "location", "job_type",
        "date_posted", "interval", "min_amount", "max_amount", "currency",
        "is_remote", "num_urgent_words", "benefits", "emails", "description"])

        keywords = search_setting['keywords']
        jobs = empty_jobs

        ss_path = os.path.join("users", username, date, search_setting['name'])
        ss_out_path = os.path.join("output", username, date, search_setting['name'])
        keywords_left = self.update_keywords_left(keywords, ss_out_path)

        while keywords_left:
            keyword = random.choice(keywords_left)
            
            kw_path = os.path.join(ss_out_path, f"{keyword}.csv")
            #kw_out_path = os.path.join(ss_out_path, f"{keyword}.csv")

            logger.info(f"Keyword: *** {keyword} *** -> Starting search...")

            try:
                jobs = scrape_jobs(
                    site_name=search_setting['site_name'],
                    search_term=keyword,
                    location=search_setting.get('location'),
                    proxy=self.proxy,
                    hours_old=search_setting['hours_old'],
                    is_remote=search_setting['is_remote'],
                    results_wanted=search_setting['results_wanted'],
                    country_indeed=search_setting['country_indeed']
                )
            except Exception as e:
                logger.error(f"Error with keyword: {keyword}")
                logger.error(f"{e}")
                if "Bad proxy" in str(e):
                    logger.critical("Bad proxy, stopping the program")
                    return False
                elif "Could not find any results for the search" in str(e):
                    logger.warning(f"No jobs found for keyword: {keyword}. Writing empty file...")
                    empty_jobs.to_csv(kw_path, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
                    keywords_left = self.update_keywords_left(keywords, ss_out_path)
                continue

            logger.info(f"Number of jobs found: {len(jobs)}")
            if not jobs.empty:
                jobs = jobs.drop_duplicates(subset=["job_url"], keep="first")
            
            if jobs.empty:
                logger.info(f"No jobs found for keyword: {keyword}. Writing empty file...")
                empty_jobs.to_csv(kw_path, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            else:
                logger.info(f"Writing jobs to file: {kw_path}")
                jobs.to_csv(kw_path, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            
            keywords_left = self.update_keywords_left(keywords, ss_out_path)
        return True

    def run_user(self, user_config: dict) -> None:
        username = user_config['user']
        logger.info(f"Running user: {username}")
        
        successful_run = []

        try:
            search_settings = user_config['search_settings']
        except KeyError:
            logger.error(f"User: {username} - No search settings found - Key Error")
            return

        if not search_settings:
            logger.error(f"User: {username} - No search settings found - Empty List")
            return

        for search_setting in user_config['search_settings']:
            date_path = os.path.join("output", username, self.date_run)
            search_setting_path = os.path.join(date_path, search_setting['name'])

            if not os.path.exists(date_path):
                os.makedirs(date_path)
                logger.info(f"Created folder: {date_path}")
            if not os.path.exists(search_setting_path):
                os.makedirs(search_setting_path)
                logger.info(f"Created folder: {search_setting_path}")

            logger.info(f"Running search setting: {search_setting['name']} for user: {username}")
            successful_run.append(self.run_search_setting(username, search_setting, self.date_run))

        if all(successful_run):
            logger.info(f"User: {username} - All search settings ran successfully")
        else:
            logger.warning(f"User: {username} - Some search settings failed. Run is incomplete")
