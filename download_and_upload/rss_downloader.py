#!/usr/bin/python
import feedparser
import sys
import re
import pandas as pd
import os.path
from os import path
import os
# adapted and translated to python3 from http://3adly.blogspot.com/2015/12/download-rss-media-files-using-python.html


def update_rss(rss_url, csv_filepath):
    print("fetching RSS data...")
    feed = feedparser.parse(rss_url)
    episodes = []
    for entry in feed.entries:
        episode = {}
        episode["title"] = entry.title
        episode["summary"] = entry.summary
        episode["image"] = entry.image.href
        links = entry.links
        for link in links:
            if link.type == u'audio/mpeg':
                episode["url"] = link.href
        episode["uploaded"] = False
        episode["sped_up_by"] = None
        episodes.append(episode)
    df = pd.DataFrame(episodes)
    # if the db already exists, update it
    if path.exists(csv_filepath):
        df_old = pd.read_csv(csv_filepath)
        df_merged = pd.concat((df_old, df))
        # drop duplicates, making sure that we select the duplicate with uploaded = True in case of conflict
        df_merged = df_merged.iloc[df_merged.uploaded.ne("uploaded").argsort(kind='mergesort')].drop_duplicates(["url", "title"])
        df_merged.to_csv(csv_filepath, index=False) #no unamed column
    # if we have no db, create it
    if not path.exists(csv_filepath):
        df.to_csv(csv_filepath, index=False) #no unamed column
    print("Done !")



if __name__ == """__main__""":
    #
    # Take url and directory parameters from user call
    #
    url = "https://rationallyspeakingpodcast.libsyn.com/rss"
    #url = "http://cowenconvos.libsyn.com/rss"
    #url = "https://feeds.feedburner.com/80000HoursPodcast"
    csv_filepath = "podcasts_db/rationally_speaking.csv"
    update_rss(url, csv_filepath)

