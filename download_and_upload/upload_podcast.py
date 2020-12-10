import pandas as pd
from download_and_upload.anchor_connect import upload_one_episode
from download_and_upload.utils import download
from audio_treatment.speedup_functions import pipeline
from audio_treatment.speedup import create_parser
import os
import time

def upload_all_podcast_from_db(podcast_db, anchor_login, anchor_password):
    start_time = time.time()
    df = pd.read_csv(podcast_db)
    df_to_upload = df[~df["uploaded"]] #only upload those we haven't already uploaded
    df_to_upload.sort_index(axis=0, ascending=False, inplace=True) #upload in chronological order
    print("{} episodes to upload...".format(len(df_to_upload)))
    counter = 0 #index does not provide a good counter
    for index, episode in df_to_upload.iterrows():
        try:
            #download podcast and image temporarly
            print("Downloading the episode from the rss feed... ({} / {})".format(counter, len(df_to_upload)))

            original_file_name, original_file_extension = download(episode.url, "temp_folder", "audio", preserve_extension = True)
            download(episode.image, "temp_folder", "image.jpg")
            #do the speaker diarization and the speedup
            print("Transforming the audio file...")
            parser = create_parser()
            args = parser.parse_args(['-f', 'temp_folder/{}'.format(original_file_name),
                                      '-auto',
                                      '-save', 'temp_folder/audio_transformed.{}'.format(original_file_extension)])
            speeds = pipeline(args)
            print("Uploading to Anchor...")
            description = episode.summary + "\n Sped up the speakers by {}".format(speeds)
            successful_upload = upload_one_episode('temp_folder/audio_transformed.mp3', 'temp_folder/image.jpg', episode.title, description, anchor_login, anchor_password)
            if successful_upload:
                df.loc[[index], ["uploaded"]] = True
                df.loc[[index], ["sped_up_by"]] = ", ".join([str(speed) for speed in speeds])
                df.to_csv(podcast_db, index=False)
            print("Removing temporary files...")
            os.remove('temp_folder/audio.mp3')
            os.remove('temp_folder/audio_transformed.mp3')
            os.remove('temp_folder/image.jpg')
            print("Done !")
        except Exception as e:
            print("Error")
            print(e)
            print("This episode will not be updated, moving on to the next")
            print("Careful, this can shuffle episode order in the RSS flux")
        counter += 1
    print("Done ! (took {} seconds)".format(int(time.time() - start_time)))





if __name__ == """__main__""":
    db = "podcasts/podcasts_db/cwt.csv"
    upload_all_podcast_from_db(db, "cwtspeedup@protonmail.com", "cwtspeedup2324")

