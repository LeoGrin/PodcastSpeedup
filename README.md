This package allows to speed up a podcast differently for each speaker. It automatically recognizes the different speakers in the podcast and speed each one up to equalize their speeds (or to the choosing of the user). 
There are two ways to use this package:
- Simply suscribing to the RSS links on your favorite podcast app (no need to install the package)
- Directly changing the speaker speeds of an audio file.

## RSS feeds

### Suscribing 
Simply check [the list of available podcasts](https://github.com/LeoGrin/PodcastSpeedup/blob/master/RSS_links.txt) and 
suscribe to the one you want on your podcast app. For each podcast, the speeds of the speakers are equalized by 
speeding up the slowest. If the podcast you want is not available, you can add a new podcast to the list.


### Adding a podcast

To add a podcast to the list so that it's downloaded, transformed and uploaded to a new RSS link:
- create an [Anchor](https://anchor.fm/) account (with a new email adress)
    
- [find the rss link of this Anchor account](https://help.anchor.fm/hc/en-us/articles/360027712351-Locating-your-Anchor-RSS-feed)
    
- run the following command with your own parameters (this is an example for the podcast Conversation With Tyler)

`python download_and_upload/add_podcast.py --name Conversation With Tyler --short-name cwt --original-rss http://cowenconvos.libsyn.com/rss --new-rss https://anchor.fm/s/3b3f2bb4/podcast/rss --anchor-username cwtspeedup@protonmail.com --anchor-password cwtspeedup2324`

`original_rss` should be the RSS link of the original podcast, `new_rss` should be the RSS link of the Anchor account you've created.

- (optional) run `python download_and_upload/refresh.py ` to transform the episodes on you computer and upload them to Anchor. It might take a long time, but it helps!

- make a pull request with all the files which have been changed.


## Transforming audio files manually
You can also use this package directly to transform podcast audio files. In this case, you'll need to install it first.

### Installing

#### Sox
SoX version 14.4.2 or higher should be installed.

To install SoX on Mac with Homebrew:

`brew install sox`

on Linux:

`apt-get install sox`

or install from [source](https://sourceforge.net/projects/sox/files/sox/).

#### DeepSpeech models
You'll need to download DeepSpeech models. Simply run:

`wget -P models/ -i models/model_links.txt`

When SoX is installed and the DeepSpeech models are downloaded, use `pip install -r requirements.txt` to install the required packages. You're done!



### Usage

`python audio_treatment/speedup.py -f INPUT_FILE -s SPEED_SPEAKER_1 SPEED_SPKEAKER_2 -save OUTPUT_FILE`

Speed-up the speakers in the input file by x2 and x1.3 (in order of appearance of each speaker), and save the result to the output file.

### Options:

`--show-speakers` : play an extract of each speaker before asking the user to choose speeds

`--automatic` : automatically match the speeds of each speakers (by speeding up the slowest). Can be useful to balance your podcasts before adjusting speed in your favorite podcast app.


### Example:

Try `python audio_treatment/speedup.py -f audio-files/tyler-trimmed.wav -s 1.8 1.2 -save results/tyler-sped-up.wav` to speed up an extract from Conversation With Tyler.

### Notes:

The package is quite slow right now (30 minutes for a 1h30 podcast)

By default, the speakers are ordered according to their first appearance in the podcast. Given that the host of the podcast is probably the first speaker, `-s 2 1.3` should speed-up the host x2 and the guest x1.3. Note that intro music can sometimes mess the default order of the speakers (to be solved).

Uses [pysox](https://github.com/rabitt/pysox) for sound modification, [pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis) for speaker diarization, [DeepSpeech](https://github.com/mozilla/DeepSpeech) for infering speaker speed in automatic mode, and [Anchor](https://anchor.fm/) for storage and RSS feeds.
