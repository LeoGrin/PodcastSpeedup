from pydub import AudioSegment
sound = AudioSegment.from_mp3("tyler.mp3")
#sound = sound[60*1000:20*60*1000]
sound.export("tyler-full.wav", format="wav")