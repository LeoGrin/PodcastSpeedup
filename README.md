This package allows to speed-up a podcast differently for each speaker. It automatically recognizes the different speakers in the podcast and speed-up each one according to the user's wish.

### Installing
SoX version 14.4.2 or higher should be installed.

To install SoX on Mac with Homebrew:

`brew install sox`

on Linux:

`apt-get install sox`

or install from [source](https://sourceforge.net/projects/sox/files/sox/).


When SoX is installed, use `pip install -r requirements.txt` to install the required packages.




### Usage

`python speedup.py -f INPUT_FILE -s 2 1.3 -save OUTPUT_FILE`

Speed-up the speakers in the input file by x2 and x1.3 (in order of appearance of each speaker), and save the result to the output file.

### Options:

`--show-speakers` : play an extract of each speaker before asking the user to choose speeds

`--automatic` : automatically match the speeds of each speakers (by speeding up the slowest). Can be useful to balance your podcasts before adjusting speed in your favorite podcast app. WARNING : experimental.


### Example:

Try `python speedup.py -f audio-files/tyler-trimmed.wav -s 1.8 1.2 -save results/tyler-sped-up.wav` to speed up an extract from Conversation With Tyler.

### Notes:

The package is quite slow right now (10 minutes for a 1h30 podcast)

By default, the speakers are ordered according to their first appearance in the podcast. Given that the host of the podcast is probably the first speaker, `-s 2 1.3` should speed-up the host x2 and the guest x1.3. Note that intro music can sometimes mess the default order of the speakers (to be solved).

Uses [pysox](https://github.com/rabitt/pysox) for sound modification, [pyAudioAnalysis](https://github.com/tyiannak/pyAudioAnalysis) for speaker diarization, and [SpeechRecognition](https://github.com/Uberi/speech_recognition) for infering speaker speed in automatic mode.
