from pyAudioAnalysis.audioSegmentation import speaker_diarization
import numpy as np
import itertools
from pydub import AudioSegment
from pydub.playback import play
from pydub.effects import speedup

#sound = AudioSegment.from_mp3("tyler.mp3")

filename = "audio-files/tyler.wav"
sound = AudioSegment.from_wav(filename)



#res = [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0]

def sound_to_chuncks(diarization, chunck_size):
    """

    :param diarization: list of speaker for each time chuck
    :param chunk_size: size of each step in diarization (in seconds)
    :return: list of segments of sound corresponding to one speaker, list of speaker for each segment
    """
    diarization = np.array(diarization)
    indice_list = np.concatenate((np.where(np.diff(diarization))[0], [len(diarization) - 1]))
    speaker_list = np.array(diarization[indice_list]).astype("int")
    print(speaker_list)
    chunck_list = []
    for i in range(len(indice_list)):
        if i == 0:
            segment_left = 0
        else:
            segment_left = (indice_list[
                                i - 1] + 1) * chunck_size * 1000  # left bound of the speaker segment (convert into milliseconds for pydub)
            # + 1 is to count the first chunk
        segment_right = (indice_list[
                             i] + 1) * chunck_size * 1000  # right bound of the speaker segment (convert into milliseconds for pydub)
        chunck = sound[segment_left:segment_right]
        chunck_list.append(chunck)
    return chunck_list, speaker_list

def show_speakers(sound, chunck_list, speaker_list, extract_length=10):
    speakers = np.unique(speaker_list)
    for speaker in speakers:
        # choose the longest chunck from the speaker (this way we'll be able to take an extract for sure)
        print(np.where(speaker_list==speaker)[0])
        print(len(chunk_list))
        speaker_chuncks = [chunk_list[i] for i in np.where(speaker_list==speaker)[0]]
        speaker_chunck = speaker_chuncks[np.argmax([len(chunck) for chunck in speaker_chuncks])]
        # play an extract from this chunck
        print("speaker {}".format(speaker))
        play(speaker_chunck[:min(extract_length*1000, len(speaker_chunck)-1)])


def speedup_speakers(sound, chunk_list, speaker_list, speeds):
    """
    :param sound: sound to be modified
    :param chunk_list: list of segment of sounds corresponding to each speaker
    :param speaker_list: list of speaker (corresponds to chunck_list)
    :param speeds: list of speed for each speaker
    :return: sound object sped up differently for each speaker
    """
    fast_chuck_list = []
    for i, chunck in enumerate(chunk_list):
        speaker = speaker_list[i]
        chunck = speedup(chunck, speeds[speaker], chunk_size=30, crossfade=150)
        fast_chuck_list.append(chunck)
    fast_sound = sum(fast_chuck_list)
    play(fast_sound)


print("diarization...")
chunck_size = 1 # in seconds, default
res = speaker_diarization(filename, n_speakers=2, mid_step=chunck_size)
print("building segments...")
chunk_list, speaker_list = sound_to_chuncks(res, chunck_size)
#print("speeding up...")
#speedup_speakers(sound, chunk_list, speaker_list, [2, 1.3])
print("showing speakers..")
show_speakers(sound, chunk_list, speaker_list)
