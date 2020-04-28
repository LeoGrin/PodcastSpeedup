from pyAudioAnalysis.audioSegmentation import speaker_diarization
from time import time
filename = "audio-files/tyler.wav"

chunck_size = 0.1 # in seconds, default
t = time()
res = speaker_diarization(filename, n_speakers=2, mid_step=chunck_size, mid_window=1.0)
print(res)
print(chunck_size)
print(time() - t)

chunck_size = 1 # in seconds, default
t = time()
res = speaker_diarization(filename, n_speakers=2, mid_step=chunck_size)
print(res)
print(chunck_size)
print(time() - t)

chunck_size = 10 # in seconds, default
t = time()
res = speaker_diarization(filename, n_speakers=2, mid_step=chunck_size)
print(res)
print(chunck_size)
print(time() - t)

