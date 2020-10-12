import pandas as pd
from download_and_upload.anchor_connect import upload_podcast
from download_and_upload.utils import download
from audio_treatment.speedup_functions import pipeline
from audio_treatment.speedup import create_parser
import tqdm
import os
import time

def upload_all_podcast_from_db(podcast_db, anchor_login, anchor_password):
    start_time = time.time()
    df = pd.read_csv(podcast_db)
    df = df[~df["uploaded"]] #only upload those we haven't already uploaded
    for index, episode in tqdm.tqdm(df.iterrows()):
        #TODO check order
        #download podcast and image temporarly
        print("Downloading the episode from the rss feed...")
        download(episode.url, "../temp_folder", "audio.mp3")
        download(episode.image, "../temp_folder", "image.jpg")
        #do the speaker diarization and the speedup
        print("Transforming the audio file...")
        #parser = create_parser()
        #args = parser.parse_args(['-f', '../temp_folder/audio.mp3', '-auto', '-save', '../temp_folder/audio_transformed.mp3'])
        #pipeline(args)
        print("Uploading to Anchor...")
        upload_podcast('../temp_folder/audio.mp3', '../temp_folder/image.jpg', episode.title, episode.summary, anchor_login, anchor_password)
        print("Removing temporary files...")
        os.remove('../temp_folder/audio.mp3')
        os.remove('../temp_folder/audio_transformed.mp3')
        print("Done !")
    print("Done ! (took {} seconds)".format(int(time.time() - start_time)))





if __name__ == """__main__""":
    db = "podcasts_db/rationally_speaking.csv"
    upload_all_podcast_from_db(db, "leo.grinsztajn@gmail.com", "7Nathanleomax61")

