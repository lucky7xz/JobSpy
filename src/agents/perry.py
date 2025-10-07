import os
import glob
import pandas as pd
import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)

class Agent_Perry:
    def __init__(self, user_configs):
        logger.info(" / ***Agent Perry is online *** /")
        logger.info("Instantiating Perry...")
        self.user_configs = user_configs
        self.perrys_todo = self.get_perrys_todo()

    def get_perrys_todo(self) -> dict:
        logger.info(" ---> Getting Perry's To-Do List...")
        perrys_todo = {}

        for user_config in self.user_configs:
            username = user_config['user']
            try:
                search_settings_user = [search_settings['name'] for search_settings in user_config['search_settings']]
                perrys_todo[username] = {}
            except KeyError:
                logger.error(f"User: {username} - No search settings found - Key Error")
                continue

            if not search_settings_user:
                logger.warning(f"User: {username} - No search settings found - Empty List")
                continue
            
            dates = glob.glob(f'users/{username}/*')
            dates = [os.path.basename(date) for date in dates if "." not in date]

            for date in dates:
                search_setting_folder_paths = glob.glob(f'users/{username}/{date}/*')
                search_setting_folder_paths = [folder for folder in search_setting_folder_paths if "." not in folder]
                perrys_todo[username][date] = search_setting_folder_paths

            for user, scraper_runs in perrys_todo.items():
                logger.info("\n --- Destination folders for {user}: ---")
                for date_entry, search_setting_folders in scraper_runs.items():
                    destination_folder = os.path.join('users', user, date_entry)
                    logger.info(f"{destination_folder}")
                    
                    for search_setting_folder in search_setting_folders:
                        search_name = os.path.basename(search_setting_folder)
                        if search_name in search_settings_user:
                            logger.info(f"    - {os.path.basename(search_setting_folder)} --- OK")
                        else:
                            logger.error(f"    - {os.path.basename(search_setting_folder)} --- NOT FOUND")
                            return {{}}
        return perrys_todo

    def daily_aggregate(self) -> None:
        logger.info(" ---> Creating Daily Aggregates...")
        for user, scraper_runs in self.perrys_todo.items():
            logger.info("\n --- Aggregating data for {user}: ---")
            for date_entry, search_setting_folders in scraper_runs.items():
                destination_folder = os.path.join('users', user, date_entry)
                template = pd.DataFrame(columns=[ "job_url",
                            "site", "title", "company", "company_url", "location", "job_type",
                            "date_posted", "interval", "min_amount", "max_amount", "currency",
                            "is_remote", "num_urgent_words", "benefits", "emails", "description",
                            "user","date","SS","KW"])
                                
                for search_setting_folder in search_setting_folders:
                    files_to_concat = glob.glob(f"{search_setting_folder}/*.csv")

                    for file in files_to_concat:
                        try:
                            read_df = pd.read_csv(file)
                            if read_df.empty:
                                logger.warning(f"    - {os.path.basename(file)} --- EMPTY")
                                continue
                            read_df["user"] = user
                            read_df["date"] = date_entry
                            read_df["SS"] = os.path.basename(search_setting_folder)
                            read_df["KW"] = os.path.basename(file).replace(".csv", "")
                            template = pd.concat([template, read_df])
                        except pd.errors.EmptyDataError:
                            logger.warning(f"    - {os.path.basename(file)} --- EMPTY (pandas error)")
                            continue
                
                template = template.drop_duplicates("job_url", keep="first")
                template = template.drop_duplicates(subset=["title", "company"], keep="first")
                template.to_csv(f"{destination_folder}/agg.csv", index=False)

    def agg_the_agg(self) -> None:
        logger.info(" ---> Aggregating the Aggregates...")
        for user in self.perrys_todo:
            agg_files = glob.glob(f"output/{user}/**/agg.csv")
            if not agg_files:
                logger.warning(f"    - No Aggregates found for {user}")
                continue

            logger.info("\n --- Aggregating Aggregates for {user}: ---")
            agg_df = pd.DataFrame(columns=[ "job_url",
                            "site", "title", "company", "company_url", "location", "job_type",
                            "date_posted", "interval", "min_amount", "max_amount", "currency",
                            "is_remote", "num_urgent_words", "benefits", "emails", "description",
                            "user","date","SS","KW"])
            
            for agg_file in agg_files:
                read_df = pd.read_csv(agg_file)
                agg_df = pd.concat([agg_df, read_df])

            agg_df.drop(["interval", "min_amount", "max_amount", "currency",
                            "num_urgent_words", "benefits", "emails", "description"], axis=1, inplace=True)
        
            agg_df = agg_df.sort_values(by="date", ascending=True)
            agg_df = agg_df.drop_duplicates("job_url", keep="first")
            agg_df = agg_df.drop_duplicates(subset=["title", "company"], keep="first")

            cols_to_order = ['date_posted', 'is_remote', 'user', 'date', 'SS', 'KW']
            new_columns = cols_to_order + [col for col in agg_df.columns if col not in cols_to_order]
            agg_df = agg_df[new_columns]

            agg_df.to_csv(f"output/{user}/agg_agg.csv", index=False)
            
            final_date = agg_df["date"].max()
            agg_df_quo = agg_df[agg_df["date"] == final_date]
            agg_df_quo.to_csv(f"output/{user}/agg_agg_today.csv", index=False)
            
            list_of_links = agg_df_quo["job_url"].tolist()
            logger.info(f"Found {len(list_of_links)} new jobs for {user}")

    def send_post_request(self, data):
        # This is a placeholder for sending a post request
        # you can replace this with your actual post request logic
        try:
            # response = requests.post("your_endpoint_url", json=data)
            # response.raise_for_status()
            logger.info(f"Sent post request with data: {data}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send post request: {e}")
