from pyAudioAnalysis.audioSegmentation import speaker_diarization
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
import argparse




def make_diarization_chronological(diarization):
    """
    :param diarization: list of ints representing the speaker of each chunk
    :return: list of ints representing the speaker of each chunk, with the speaker being indexed in chronological order
    """
    u, indices = np.unique(diarization, return_index=True) # we use the fact that np.unique(, return_index=True)
    # return first index of appearance
    conversion_table = np.argsort(indices)
    return [conversion_table[speaker] for speaker in diarization]



def sound_to_chunks(sound, diarization, chunk_size):
    """

    :param diarization: list of speaker for each time chuck
    :param chunk_size: size of each step in diarization (in seconds)
    :return: list of segments of sound corresponding to one speaker, list of speaker for each segment
    """
    diarization = np.array(diarization)
    indice_list = np.concatenate((np.where(np.diff(diarization))[0], [len(diarization) - 1]))
    speaker_list = np.array(diarization[indice_list]).astype("int")
    chunk_list = []
    for i in range(len(indice_list)):
        if i == 0:
            segment_left = 0
        else:
            segment_left = (indice_list[i - 1] + 1) * chunk_size * 1000  # left bound of the speaker segment
            # (convert into milliseconds for pydub) (+ 1 is to count the first chunk)
        segment_right = (indice_list[i] + 1) * chunk_size * 1000  # right bound of the speaker segment
        chunk = sound[segment_left:segment_right]
        chunk_list.append(chunk)
    return chunk_list, speaker_list

def show_speakers(chunk_list, speaker_list, extract_length=10):
    speakers = np.unique(speaker_list)
    for speaker in speakers:
        # choose the longest chunk from the speaker (this way we'll be able to take an extract for sure)
        speaker_chunks = [chunk_list[i] for i in np.where(speaker_list == speaker)[0]]
        speaker_chunk = speaker_chunks[np.argmax([len(chunk) for chunk in speaker_chunks])]
        # play an extract from this chunk
        print("Listening to speaker {}".format(speaker))

        play(speaker_chunk[:min(extract_length*1000, len(speaker_chunk)-1)])


def speedup_speakers(chunk_list, speaker_list, speeds):
    """
    :param sound: sound to be modified
    :param chunk_list: list of segment of sounds corresponding to each speaker
    :param speaker_list: list of speaker (corresponds to chunk_list)
    :param speeds: list of speed for each speaker
    :return: sound object sped up differently for each speaker
    """
    fast_chuck_list = []
    for i, chunk in enumerate(chunk_list):
        speaker = speaker_list[i]
        chunk = speedup(chunk, speeds[speaker], chunk_size=30, crossfade=150)
        fast_chuck_list.append(chunk)
    fast_sound = sum(fast_chuck_list)
    play(fast_sound)

def pipeline(args):
    #TODO : convert if not wav
    print("loading file...")
    sound = AudioSegment.from_wav(args.filename)
    print("diarization...")
    diarization = np.array(speaker_diarization(args.filename, n_speakers=args.n_speakers, mid_step=args.chunk_size)).astype("int")
    diarization = make_diarization_chronological(diarization)
    print("Found {} speakers".format(len(np.unique(diarization))))
    print("building segments...")
    chunk_list, speaker_list = sound_to_chunks(sound, diarization, args.chunk_size)
    if args.show_speakers:
        print("showing speakers..")
        show_speakers(chunk_list, speaker_list)
    print("speeding up...")
    speedup_speakers(chunk_list, speaker_list, args.speeds)


#sound = AudioSegment.from_mp3("tyler.mp3")

#filename = "audio-files/tyler.wav"

#pipeline(filename)


parser = argparse.ArgumentParser(description="Speed up podcast differently for each speaker")

parser.add_argument("-f", "--filename", type=str, dest="filename", help="Path of the sound file you want to speed up", required=True)
parser.add_argument("-n", "--n_speakers", type=int, dest="n_speakers", help="Number of people speaking (0 if unkown)", default=0)
parser.add_argument("--chunk-size", type=float, dest="chunk_size", help="Size of each chunk during speaker diarization", default=0.1)
parser.add_argument("--show-speakers", type=bool, dest="show_speakers", help="Whether to play an extract of each speaker before asking for the speeds")
parser.add_argument("-s", "--speeds", nargs='+', type=float, dest="speeds", help="Speed of each speaker in the extract")

args = parser.parse_args()

pipeline(args)