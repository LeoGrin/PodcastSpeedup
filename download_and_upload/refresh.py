import pandas as pd
from download_and_upload.upload_podcast import upload_all_podcast_from_db
from download_and_upload.rss_downloader import update_rss
import os
import time

def refresh(podcasts_df_file):
    podcasts_df = pd.read_csv(podcasts_df_file)
    print("Uploading new episodes from all podcasts")
    print("{} podcasts to refresh".format(len(podcasts_df)))
    for index, podcast in podcasts_df.iterrows():
        print("Checking new episodes from {}".format(podcast.full_name))
        podcast_db = "podcasts/podcasts_db/{}.csv".format(podcast.short_name)
        update_rss(podcast.original_rss, podcast_db)
        upload_all_podcast_from_db(podcast_db, podcast.anchor_username, podcast.anchor_password)


if __name__ == """__main__""":
    podcast_df_file = "podcasts/podcasts_db/all_podcasts_db.csv"
    refresh(podcast_df_file)
