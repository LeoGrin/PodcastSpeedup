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
    df_to_upload = df[~df["uploaded"]] #only upload those we haven't already uploaded
    df_to_upload.sort_index(axis=0, ascending=False, inplace=True)
    print("{} episodes to upload...".format(len(df_to_upload)))
    counter = 0 #index does not provide a good counter
    for index, episode in df_to_upload.iterrows():
        try:
            #download podcast and image temporarly
            print("Downloading the episode from the rss feed... ({} / {})".format(counter, len(df_to_upload)))
            download(episode.url, "../temp_folder", "audio.mp3")
            download(episode.image, "../temp_folder", "image.jpg")
            #do the speaker diarization and the speedup
            print("Transforming the audio file...")
            parser = create_parser()
            args = parser.parse_args(['-f', '../temp_folder/audio.mp3', '-auto', '-save', '../temp_folder/audio_transformed.mp3'])
            pipeline(args)
            print("Uploading to Anchor...")
            successful_upload = upload_podcast('../temp_folder/audio_transformed.mp3', '../temp_folder/image.jpg', episode.title, episode.summary, anchor_login, anchor_password)
            if successful_upload:
                df.loc[[index], ["uploaded"]] = True
                df.to_csv(podcast_db, index=False)
            print("Removing temporary files...")
            os.remove('../temp_folder/audio.mp3')
            os.remove('../temp_folder/audio_transformed.mp3')
            print("Done !")
        except Exception as e:
            print("Error")
            print(e)
            print("This episode will not be updated, moving on to the next")
            print("Careful, this can shuffle episode order in the RSS flux")
        counter += 1
    print("Done ! (took {} seconds)".format(int(time.time() - start_time)))





if __name__ == """__main__""":
    db = "podcasts_db/cwt.csv"
    upload_all_podcast_from_db(db, "cwtspeedup@protonmail.com", "cwtspeedup2324")

