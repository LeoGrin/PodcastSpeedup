from pydub import AudioSegment
sound = AudioSegment.from_file("tyler.wav")
from pydub.playback import play
from pydub.effects import speedup


def speed_change(sound, speed=1.0):
    # Manually override the frame_rate. This tells the computer how many
    # samples to play per second
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
         "frame_rate": int(sound.frame_rate * speed)
      })
     # convert the sound with altered frame rate to a standard frame rate
     # so that regular playback programs will work right. They often only
     # know how to play audio at standard frame rate (like 44.1k)
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)


#slow_sound = speed_change(sound, 0.75)
fast_sound = speedup(sound, 2, chunk_size=30, crossfade=150)
fast_sound.export("tyler-fast.wav", format="wav")