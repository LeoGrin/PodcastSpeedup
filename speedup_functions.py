from pyAudioAnalysis.audioSegmentation import speaker_diarization
import numpy as np
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


# TODO convert

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
            segment_left = (indice_list[i - 1] + 1) * chunk_size  # left bound of the speaker segment
            # + 1 is to count the first chunk
        segment_right = (indice_list[i] + 1) * chunk_size  # right bound of the speaker segment
        segment_list.append((segment_left, segment_right))
    print(segment_list)
    return segment_list, speaker_list


def transform(segment_list, speaker_list, speeds, input_file, temp_file="temp_folder/temp"):
    """
    Speed up each segment of sound and save the sped-up segment to a temporary file
    :param segment_list:
    :param speaker_list:
    :param speeds:
    :param input_file:
    :param temp_file:
    :return:
    """
    temp_paths = []
    for i, segment in tqdm(enumerate(segment_list)):
        tfm = sox.Transformer()
        tfm.trim(segment[0], segment[1])
        tfm.tempo(speeds[speaker_list[i]], "s")
        tfm.build(input_file, temp_file + str(i) + ".wav")
        temp_paths.append(temp_file + str(i) + ".wav")

    return temp_paths


def combine(temp_paths, output_file, keep_files=False):
    """
    Works with transform. Combine the temporary files into one and delete them afterwards.
    :param temp_paths: path of the files used to store the files to be combined
    :param output_file: path where we save the combined file
    :param keep_files: whether to keep the temporary files to be combined (default is False)
    :return: None
    """
    cmb = sox.Combiner()
    cmb.build(temp_paths, output_file, combine_type="concatenate")
    if not keep_files:
        for file in temp_paths:
            os.remove(file)


def speed_up(segment_list, speaker_list, speeds, input_file, temp_file="temp_folder/temp",
             output_file="results/final_result.wav"):
    """
    Speed up the input file differently for each speaker
    :param segment_list: list of segment of sounds ((tuple of time coordinate) corresponding to each speaker
    :param speaker_list: list of speaker (corresponds to segment_list)
    :param speeds: speed augmentation for each speaker (multiplicative)
    :param input_file: File to be sped-up
    :param temp_file: where to store the temporary files
    :param output_file: where to store the result of the speed-up
    :return: None
    """
    output_paths = transform(segment_list, speaker_list, speeds, input_file, temp_file)
    combine(output_paths, output_file, keep_files=True)


def show_speakers(input_file, segment_list, speaker_list, extract_length=10):
    """
    Play an extract of each speaker so the user to help the user choose the speeds
    :param input_file: file to be used
    :param segment_list: list of segment of sounds (tuple of time coordinate) corresponding to each speaker
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


def create_speaker_sample(input_file, segment_list, speaker_list, max_length=60, min_length=500):
    """
    Create a representative extract of each speaker in the diarized audio file
    :param input_file (list): name of the file to use
    :param segment_list (list): list of segment of sounds (tuple of time coordinate) corresponding to each speaker
    :param speaker_list (list): list of speaker (corresponds to segment_list)
    :param max_length (float): maximum length of a single extract of a speaker to use in the full sample (for variety)
    :param min_length (float): minimum length of the final sample
    :return: List of tuples (path_to_sample, length_of_exrtact) for each speaker
    """
    filename = input_file.split(".")[0].split("/")[-1]
    speakers_output = [] # list of tuple (path_to_sample, length_of_exrtact) for each speaker
    speakers = np.unique(speaker_list)
    for speaker in speakers:
        speaker_segments = [segment_list[i] for i in np.where(speaker_list == speaker)[0]]
        speaker_segment_length = [(segment[1] - segment[0]) for segment in speaker_segments]
        speaker_segment_indices = np.argsort(speaker_segment_length)[::-1]  # from longest to shortest
        total_length = 0  # length of all extracts we use from this speaker
        i = 0
        outputs = []
        while total_length < min_length:  # we concatenate different extract of the speaker until we have enough length
            tfm = sox.Transformer()
            speaker_segment = speaker_segments[speaker_segment_indices[i]]
            segment_length = min(max_length, speaker_segment[1] - speaker_segment[0])
            total_length += segment_length
            tfm.trim(speaker_segment[0], speaker_segment[0] + segment_length)
            # tfm.preview(input_file)
            tfm.build(input_file, "temp_folder/temp_speed_" + str(speaker) + str(i) + filename + ".wav")
            outputs.append("temp_folder/temp_speed_" + str(speaker) + str(i) + filename + ".wav")
            i += 1
        # Now that we have a representative extract, we transcribe it to infer the speed of the speaker.

        print("Speaker " + str(speaker))
        print("Number of detected extracts : " + str(len(speaker_segment_indices)))
        print("Length of combined extracts : " +str(total_length))
        print("Number of selected extracts : " + str(len(outputs)))

        if len(outputs) > 1:
            cmb = sox.Combiner()
            cmb.build(outputs, "temp_folder/to_process" + str(speaker) + filename + ".wav", combine_type="concatenate")
            speakers_output.append(("temp_folder/to_process" + str(speaker) + filename + ".wav", total_length))
            for file in outputs:
                os.remove(file)  # remove temporary files
        else:
            speakers_output.append((outputs[0], total_length))

    return speakers_output


def find_speaker_speeds(input_file, segment_list, speaker_list, max_length=40, min_length=40):
    """
    Find speed for each speaker by looking at the number of syllab pronounced by unit of time. Use DeepSpeech.
    Delete the file in speakers_output !
    :param speakers_output  List of tuples (path_to_sample, length_of_exrtact) for each speaker
    :return: List of speeds (syllab / s) for each speakers.
    """
    speakers_speeds = []
    speakers_output = create_speaker_sample(input_file, segment_list, speaker_list, max_length, min_length)
    for filename, length in speakers_output:
        n_syllabs = speech_to_syllabs(filename, length)
        speakers_speeds.append(n_syllabs / length)
        os.remove(filename)
    return speakers_speeds


def convert(input_file, output_format="wav"):
    """
    Convert the input file the output format if necessary and save a new file with the right format
    :param input_file: path of input file
    :param output_format: format to output
    :return:  path to the  new file
    """
    # TODO delete file afterward
    if input_file[-3:] != output_format:
        tfm = sox.Transformer()
        new_file = input_file[:-3] + "wav"
        tfm.build(input_file, new_file)
    else:
        new_file = input_file

    return new_file


def pipeline(args):
    start_time = time.time()
    args.filename = convert(args.filename)
    t = time.time()
    print("diarization...")
    diarization = np.array(speaker_diarization(args.filename, n_speakers=args.n_speakers, mid_step=args.chunk_size,
                                               short_window=args.short_window, mid_window=args.mid_window,
                                               lda_dim=args.lda_dim)).astype("int")
    diarization = make_diarization_chronological(diarization)
    print("Done !")
    print("Took {} seconds".format(int(time.time() - t)))
    print("number of chunk : {}".format(len(diarization)))
    print("Found {} speakers".format(len(np.unique(diarization))))
    print("building segments...")
    segment_list, speaker_list = sound_to_segments(diarization, args.chunk_size)
    if args.show_speakers:
        print("showing speakers...")
        show_speakers(args.filename, segment_list, speaker_list)
        print("choose speeds for each speakers")
        args.speeds = np.array(input().split(" ")).astype(float)
    if args.auto:
        print("Automatically finding speakers speeds...")
        speeds = find_speaker_speeds(args.filename, segment_list, speaker_list)
        print("Speakers speeds: (syllab / minutes)")
        print(list(60 * np.array(speeds))) # convert to syllab / minutes
        args.speeds = [max(speeds) / speed for speed in speeds]
        print("Going to speed up the speakers by :")
        print(args.speeds)
    print("speeding up...")
    speed_up(segment_list, speaker_list, args.speeds, args.filename, output_file=args.save_file)
    print("Done in {} seconds! Saved the result to {}".format(int(time.time() -start_time), args.save_file))
