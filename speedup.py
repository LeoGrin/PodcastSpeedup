from pyAudioAnalysis.audioSegmentation import speaker_diarization
import numpy as np
import argparse
import sox
import os
import time
from tqdm import tqdm
from speech_to_text import *



def make_diarization_chronological(diarization):
    """
    :param diarization: list of ints representing the speaker of each chunk
    :return: list of ints representing the speaker of each chunk, with the speaker being indexed in chronological order
    """
    u, indices = np.unique(diarization, return_index=True) # we use the fact that np.unique(, return_index=True)
    # return first index of appearance
    conversion_table = np.argsort(indices)
    return [conversion_table[speaker] for speaker in diarization]

#TODO convert

# def play_chunks(chunk_list, speaker_list):
#     """
#     Play each chunk of sound segmented by speaker (mostly for debugging purpose)
#     :param chunk_list: list of segment of sounds corresponding to each speaker
#     :param speaker_list: list of speaker (corresponds to chunk_list)
#     :return: None
#     """
#     for i, chunk in enumerate(chunk_list):
#         print("Listening to speaker {}".format(speaker_list[i]))
#         play(chunk)

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
    for i in tqdm(range(len(indice_list))):
        if i == 0:
            segment_left = 0
        else:
            segment_left = (indice_list[i - 1] + 1) * chunk_size   # left bound of the speaker segment
            # + 1 is to count the first chunk
        segment_right = (indice_list[i] + 1) * chunk_size  # right bound of the speaker segment
        segment_list.append((segment_left, segment_right))
    return segment_list, speaker_list

def transform(segment_list, speaker_list, speeds, input_file, temp_file="temp_folder/temp"):
    """
    Speed up each segment of sound and save the speeded segment to a temporary file
    :param segment_list:
    :param speaker_list:
    :param speeds:
    :param input_file:
    :param temp_file:
    :return:
    """
    temp_paths = []
    speed_emp = [[], []]
    for i, segment in tqdm(enumerate(segment_list)):
        tfm = sox.Transformer()
        tfm.trim(segment[0], segment[1])
        speed_emp[speaker_list[i]].append(float(tfm.stat(input_file)["Rough frequency"]))
        tfm.tempo(speeds[speaker_list[i]], "s")
        tfm.build(input_file, temp_file + str(i) + ".wav")
        temp_paths.append(temp_file + str(i) + ".wav")
    print(np.mean(speed_emp[0]))
    print(np.mean(speed_emp[1]))
    print(speed_emp)
    return temp_paths

def combine(temp_paths, output_file="results/final_result.wav", keep_files=False):
    """
    Works with transform. Combine the temporary files into one and delete them afterwards.
    :param temp_paths:
    :param output_file:
    :param keep_files:
    :return:
    """
    cmb = sox.Combiner()
    cmb.build(temp_paths, output_file, combine_type="concatenate")
    if not keep_files:
        for file in temp_paths:
            os.remove(file)

def speed_up(segment_list, speaker_list, speeds, input_file, temp_file="temp_folder/temp", output_file="results/final_result.wav"):
    """
    Speed up the input file differently for each speaker
    :param segment_list:
    :param speaker_list:
    :param speeds:
    :param input_file:
    :param temp_file:
    :param output_file:
    :return:
    """
    output_paths = transform(segment_list, speaker_list, speeds, input_file, temp_file)
    combine(output_paths, output_file)


def show_speakers(input_file, segment_list, speaker_list, extract_length=10):
    """
    Play an extract of each speaker so the user to help the user choose the speeds
    :param segment: list of segment of sounds corresponding to each speaker (tuple of time coordinate)
    :param speaker_list: list of speaker (corresponds to segment_list)
    :param extract_length: length of extracts in seconds
    :return: None
    """
    speakers = np.unique(speaker_list)
    for speaker in speakers:
        tfm = sox.Transformer()
        # choose the longest chunk from the speaker (this way we'll be able to take an extract for sure)
        speaker_segments = [segment_list[i] for i in np.where(speaker_list == speaker)[0]]
        speaker_segment_length = [(segment[1] - segment[0]) for segment in speaker_segments]
        speaker_segment = speaker_segments[np.argmax(speaker_segment_length)]
        tfm.trim(speaker_segment[0], min(speaker_segment[1], speaker_segment[0] + extract_length))
        # play an extract from this chunk
        print("Listening to speaker {}".format(speaker))
        tfm.preview(input_file)

def find_speaker_speeds(input_file, segment_list, speaker_list, max_length=60, min_length=40):
    speakers_speeds = []
    speakers = np.unique(speaker_list)
    print(speaker_list)
    for speaker in speakers:
        speaker_segments = [segment_list[i] for i in np.where(speaker_list == speaker)[0]]
        speaker_segment_length = [(segment[1] - segment[0]) for segment in speaker_segments]
        speaker_segment_indices = np.argsort(speaker_segment_length)[::-1] # from longest to shortest
        total_length = 0  # length of all extracts we use from this speaker
        i = 0
        outputs = []
        while total_length < min_length: # we concatenate different extract of the speaker until we have enough length
            tfm = sox.Transformer()
            speaker_segment = speaker_segments[speaker_segment_indices[i]]
            segment_length = min(max_length, speaker_segment[1] - speaker_segment[0])
            total_length += segment_length
            tfm.trim(speaker_segment[0], speaker_segment[0] + segment_length)
            #tfm.preview(input_file)
            tfm.build(input_file, "temp_folder/temp" + str(i) + ".wav")
            outputs.append("temp_folder/temp" + str(i) + ".wav")
            i += 1
        print(outputs)
        if len(outputs) > 1:
            cmb = sox.Combiner()
            cmb.build(outputs, "temp_folder/to_process.wav", combine_type="concatenate")
            n_syllabs = speech_to_syllabs("temp_folder/to_process.wav")
            os.remove("temp_folder/to_process.wav")
        else:
            n_syllabs = speech_to_syllabs(outputs[0])
        for file in outputs:
            os.remove(file)
        print(n_syllabs)
        print(total_length)
        speakers_speeds.append(n_syllabs / total_length)


    return speakers_speeds



def convert(input_file, output_format="wav"):
    """
    Convert the input file the output format if necessary and save a new file with the right format
    :param input_file: path of input file
    :param output_format: format to output
    :return:  path to the  new file
    """
    #TODO delete file afterward
    if input_file[-3:] != output_format:
        tfm = sox.Transformer()
        new_file = input_file[:-3] + "wav"
        tfm.build(input_file, new_file)
    else:
        new_file = input_file

    return new_file



def pipeline(args):
    args.filename = convert(args.filename)
    print("diarization...")
    diarization = np.array(speaker_diarization(args.filename, n_speakers=args.n_speakers, mid_step=args.chunk_size,
                                               short_window=args.short_window, mid_window=args.mid_window,
                                               lda_dim=args.lda_dim)).astype("int")
    diarization = make_diarization_chronological(diarization)
    print("number of chunk : {}".format(len(diarization)))
    print("Found {} speakers".format(len(np.unique(diarization))))
    print("building segments...")
    segment_list, speaker_list = sound_to_segments(diarization, args.chunk_size)
    if args.show_speakers:
        print("showing speakers..")
        show_speakers(args.filename, segment_list, speaker_list)
        print("choose speeds for each speakers")
        args.speeds = np.array(input().split(" ")).astype(float)
    if args.auto:
        speeds = find_speaker_speeds(args.filename, segment_list, speaker_list)
        args.speeds = [max(speeds) / speed for speed in speeds]
        print(args.speeds)
    print("speeding up...")
    speed_up(segment_list, speaker_list, args.speeds, args.filename)




parser = argparse.ArgumentParser(description="Speed up podcast differently for each speaker")

# Basic parameters
parser.add_argument("-f", "--filename", type=str, dest="filename", help="Path of the sound file you want to speed up", required=True)
parser.add_argument("-n", "--n_speakers", type=int, dest="n_speakers", help="Number of people speaking (0 if unkown)", default=0)
parser.add_argument("-s", "--speeds", nargs='+', type=float, dest="speeds", help="Speed of each speaker in the extract")
parser.add_argument("-save", "--save-file", type=str, dest="save_file", help="Path of the file we want to save to", default=None)

# More options
parser.add_argument('--show-speakers', dest="show_speakers", help="Whether to play an extract of each speaker before asking for the speeds", action='store_true')
parser.set_defaults(show_speakers=False)
parser.add_argument("-auto", "--automatic", dest="auto", help="Whether to automatically match the speeds of the two speakers (EXPERIMENTAL)", action='store_true')
parser.set_defaults(auto=False)

# Technical arguments for diarization
parser.add_argument("--chunk-size", type=float, dest="chunk_size", help="Size of each chunk during speaker diarization", default=0.1)
parser.add_argument("--short-window", type=float, dest="short_window", help="Crossfade for the speedup algorithm", default=0.05)
parser.add_argument("--mid-window", type=float, dest="mid_window", help="Crossfade for the speedup algorithm", default=2.0)
parser.add_argument("--lda-dim", type=int, dest="lda_dim", help="Crossfade for the speedup algorithm", default=35)

args = parser.parse_args()
t = time.time()
pipeline(args)
print(time.time() - t)