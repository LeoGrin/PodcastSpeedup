from pyAudioAnalysis.audioSegmentation import speaker_diarization
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup
import argparse
import sox
import os




def make_diarization_chronological(diarization):
    """
    :param diarization: list of ints representing the speaker of each chunk
    :return: list of ints representing the speaker of each chunk, with the speaker being indexed in chronological order
    """
    u, indices = np.unique(diarization, return_index=True) # we use the fact that np.unique(, return_index=True)
    # return first index of appearance
    conversion_table = np.argsort(indices)
    return [conversion_table[speaker] for speaker in diarization]

def play_chunks(chunk_list, speaker_list):
    """
    Play each chunk of sound segmented by speaker (mostly for debugging purpose)
    :param chunk_list: list of segment of sounds corresponding to each speaker
    :param speaker_list: list of speaker (corresponds to chunk_list)
    :return: None
    """
    for i, chunk in enumerate(chunk_list):
        print("Listening to speaker {}".format(speaker_list[i]))
        play(chunk)

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

def sound_to_segments(diarization, chunk_size):
    """
    :param diarization: list of speaker for each time chuck
    :param chunk_size: size of each step in diarization (in seconds)
    :return: list of segments of sound corresponding to one speaker, list of speaker for each segment
    """
    diarization = np.array(diarization)
    indice_list = np.concatenate((np.where(np.diff(diarization))[0], [len(diarization) - 1]))
    speaker_list = np.array(diarization[indice_list]).astype("int")
    segment_list = []
    for i in range(len(indice_list)):
        if i == 0:
            segment_left = 0
        else:
            segment_left = (indice_list[i - 1] + 1) * chunk_size   # left bound of the speaker segment
            # (convert into milliseconds for pydub) (+ 1 is to count the first chunk)
        segment_right = (indice_list[i] + 1) * chunk_size  # right bound of the speaker segment
        segment_list.append((segment_left, segment_right))
    return segment_list, speaker_list

def transform(segment_list, speaker_list, speeds, input_file, output_file):
    output_paths = []
    for i, segment in enumerate(segment_list):
        tfm = sox.Transformer()
        tfm.trim(segment[0], segment[1])
        tfm.tempo(speeds[speaker_list[i]], "s")
        tfm.build(input_file, output_file + str(i) + ".wav")
        output_paths.append(output_file + str(i) + ".wav")
    return output_paths

def combine(output_paths):
    cmb = sox.Combiner()
    cmb.build(output_paths, "temp_folder/final_result.wav", combine_type="concatenate")
    for file in output_paths:
        os.remove(file)



def show_speakers(chunk_list, speaker_list, extract_length=10):
    """
    Play an extract of each speaker so the user to help the user choose the speeds
    :param chunk_list: list of segment of sounds corresponding to each speaker
    :param speaker_list: list of speaker (corresponds to chunk_list)
    :param extract_length: length of extracts in seconds
    :return: None
    """
    speakers = np.unique(speaker_list)
    for speaker in speakers:
        # choose the longest chunk from the speaker (this way we'll be able to take an extract for sure)
        speaker_chunks = [chunk_list[i] for i in np.where(speaker_list == speaker)[0]]
        speaker_chunk = speaker_chunks[np.argmax([len(chunk) for chunk in speaker_chunks])]
        # play an extract from this chunk
        print("Listening to speaker {}".format(speaker))

        play(speaker_chunk[:min(extract_length*1000, len(speaker_chunk)-1)])


def speedup_speakers(chunk_list, speaker_list, speeds, chunk_size_speedup, crossfade):
    """
    :param sound: sound to be modified
    :param chunk_list: list of segment of sounds corresponding to each speaker
    :param speaker_list: list of speaker (corresponds to chunk_list)
    :param speeds: list of speed for each speaker
    :return: sound object sped up differently for each speaker
    """
    modified_chuck_list = []
    for i, chunk in enumerate(chunk_list):
        speaker = speaker_list[i]
        chunk = speedup(chunk, speeds[speaker], chunk_size=chunk_size_speedup, crossfade=crossfade)
        modified_chuck_list.append(chunk)
    modified_sound = sum(modified_chuck_list)
    return modified_sound

def pipeline(args):
    #TODO : convert if not wav
    print("loading file...")
    sound = AudioSegment.from_wav(args.filename)
    print("diarization...")
    diarization = np.array(speaker_diarization(args.filename, n_speakers=args.n_speakers, mid_step=args.chunk_size, short_window=args.short_window, mid_window=args.mid_window, lda_dim=args.lda_dim)).astype("int")
    diarization = make_diarization_chronological(diarization)
    print("number of chunk : {}".format(len(diarization)))
    print("Found {} speakers".format(len(np.unique(diarization))))
    print("building segments...")
    chunk_list, speaker_list = sound_to_chunks(sound, diarization, args.chunk_size)
    if args.show_speakers:
        print("showing speakers..")
        show_speakers(chunk_list, speaker_list)
    print("speeding up...")
    #play_chunks(chunk_list, speaker_list)
    result = speedup_speakers(chunk_list, speaker_list, args.speeds, args.chunk_size_speedup, args.crossfade)
    if args.play:
         play(result)
    # if args.save_file:
    #     result.export(args.save_file, format=args.format)


def pipeline_sox(args):
    # TODO : convert if not wav
    print("diarization...")
    diarization = np.array(speaker_diarization(args.filename, n_speakers=args.n_speakers, mid_step=args.chunk_size,
                                               short_window=args.short_window, mid_window=args.mid_window,
                                               lda_dim=args.lda_dim)).astype("int")
    diarization = make_diarization_chronological(diarization)
    print("number of chunk : {}".format(len(diarization)))
    print("Found {} speakers".format(len(np.unique(diarization))))
    print("building segments...")
    #chunk_list, speaker_list = sound_to_chunks(sound, diarization, args.chunk_size)
    segment_list, speaker_list = sound_to_segments(diarization, args.chunk_size)
    if args.show_speakers:
        print("showing speakers..")
        #show_speakers(chunk_list, speaker_list)
    print("speeding up...")
    # play_chunks(chunk_list, speaker_list)
    #result = speedup_speakers(chunk_list, speaker_list, args.speeds, args.chunk_size_speedup, args.crossfade)
    output_paths = transform(segment_list, speaker_list, args.speeds, "audio-files/tyler.wav", "temp_folder/test")
    combine(output_paths)
    #if args.play:
    #    play(result)
    # if args.save_file:
    #     result.export(args.save_file, format=args.format)


#sound = AudioSegment.from_mp3("tyler.mp3")

#filename = "audio-files/tyler.wav"

#pipeline(filename)


parser = argparse.ArgumentParser(description="Speed up podcast differently for each speaker")

parser.add_argument("-f", "--filename", type=str, dest="filename", help="Path of the sound file you want to speed up", required=True)
parser.add_argument("-n", "--n_speakers", type=int, dest="n_speakers", help="Number of people speaking (0 if unkown)", default=0)
parser.add_argument("--chunk-size", type=float, dest="chunk_size", help="Size of each chunk during speaker diarization", default=0.1)
parser.add_argument("--show-speakers", type=bool, dest="show_speakers", help="Whether to play an extract of each speaker before asking for the speeds", default=False)
parser.add_argument("-s", "--speeds", nargs='+', type=float, dest="speeds", help="Speed of each speaker in the extract")
parser.add_argument("--play", type=bool, dest="play", help="Whether to play audio at the end (mostly for debugging)", default=False)
parser.add_argument("-save", "--save-file", type=str, dest="save_file", help="Path of the file we want to save to", default=None)
parser.add_argument("-format", type=str, dest="format", help="Format of the saved file", default="wav")
## for testing TODO remove ?
parser.add_argument("--chunk-size-speedup", type=float, dest="chunk_size_speedup", help="Chunk size for the speedup algorithm", default=150)
parser.add_argument("-crossfade", type=float, dest="crossfade", help="Crossfade for the speedup algorithm", default=25)
parser.add_argument("--short-window", type=float, dest="short_window", help="Crossfade for the speedup algorithm", default=0.05)
parser.add_argument("--mid-window", type=float, dest="mid_window", help="Crossfade for the speedup algorithm", default=2.0)
parser.add_argument("--lda-dim", type=int, dest="lda_dim", help="Crossfade for the speedup algorithm", default=35)

args = parser.parse_args()

pipeline_sox(args)