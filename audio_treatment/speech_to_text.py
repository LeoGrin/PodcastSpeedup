import numpy as np
import re
from deepspeech import Model
import sox
import subprocess
import shlex
import os
try:
    from shhlex import quote
except ImportError:
    from pipes import quote


def speech_to_syllabs(input_file, file_length):
    """
    Compute the number of syllabs pronounced in the input file
    :param input_file: file containing the sound to analyse
    :param file_length: time length of the input file (in seconds)
    :return: the number of syllabs pronounced in the file
    """
    #t = time.time()
    words = speech_to_text(input_file, file_length, return_speed_per_chunk=False).split(" ")
    #print(time.time() - t)
    #print(len(words))
    #print(words)
    return sum([syllab_count(word) for word in words])

def speed_distribution(input_file, file_length, chunk_size=10):
    """
    Function used for experimentation, to retrieve the number of syllab in each chunk of the extract
    :param input_file: file containing the sound extract
    :param file_length: time length of the input file (in seconds)
    :param chunk_size: size of the chunk in which we decompose the sound
    :return: a list of the number of syllabs in each chunk
    """
    words_per_chunk = map(lambda s:s.split(" "),
                          speech_to_text(input_file, file_length, return_speed_per_chunk=True, chunk_size=chunk_size))
    syllabs_per_chunk = map(lambda words:sum([syllab_count(word) for word in words]),
                            words_per_chunk)
    return syllabs_per_chunk




def convert_samplerate(audio_path, desired_sample_rate):
    # taken from DeepSpeech github
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, 'SoX not found, use {}hz files or install it: {}'.format(desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)



def speech_to_text(input_file, file_length, return_speed_per_chunk=False, chunk_size = 10):
    """
    Compute the words pronounced in the input_file
    :param input_file: sound file path
    :param file_length: time length of the input file (in seconds)
    :param return_speed_per_chunk: if True, the function return a list of words per chunk, if false it returns all the words in the extract
    :return: words as string
    """
    # setup the model
    if return_speed_per_chunk:
        result = []
    else:
        result = ""
    recognizer = Model("../models/deepspeech-0.8.2-models.pbmm")
    recognizer.setBeamWidth(2000)
    recognizer.enableExternalScorer("../models/deepspeech-0.8.2-models.scorer")
    desired_sample_rate = recognizer.sampleRate()
    # convert input file into smaller audio chunks (apparently works better)
    CHUNK_SIZE = chunk_size
    n_chunks = int(file_length // CHUNK_SIZE)
    for i in range(n_chunks):
        tfm = sox.Transformer()
        tfm.trim(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE)
        tfm.set_output_format(channels=1)
        tfm.build(input_file, "../temp_folder/chunked_file{}.wav".format(i))
        cmb = sox.Combiner()
        input_list = ["../audio-files/silence.wav", "../temp_folder/chunked_file{}.wav".format(i),
                      "../audio-files/silence.wav"]
        cmb.build(input_list, "../temp_folder/chunked_file_with_silence{}.wav".format(i), combine_type="concatenate")
        fs, audio = convert_samplerate("../temp_folder/chunked_file_with_silence{}.wav".format(i), desired_sample_rate)
        if return_speed_per_chunk:
            result.append(recognizer.stt(audio))
        else:
            result += recognizer.stt(audio)
        os.remove("../temp_folder/chunked_file{}.wav".format(i))
        os.remove("../temp_folder/chunked_file_with_silence{}.wav".format(i))
    print(result)
    return result

#def speech_to_text_google(input_file):
#    """
#    Compute the words pronounced in the input_file
#    :param input_file: sound file
#    :return: words as string
#    """
    # r = sr.Recognizer()
    # with sr.AudioFile(input_file) as source:
    #     audio = r.record(source)  # read the entire audio file
    # try:
    #     return r.recognize_google(audio)
    # except sr.UnknownValueError:
    #     print("Google could not understand audio")
    # except sr.RequestError as e:
    #     print("Google error; {0}".format(e))



def syllab_count(word) :
    """
    Count syllabs in a word (from https://eayd.in/?p=232)
    :param word: word to be analysed
    :return: number of syllab
    """
    word = word.lower()

    # exception_add are words that need extra syllables
    # exception_del are words that need less syllables

    exception_add = ['serious','crucial']
    exception_del = ['fortunately','unfortunately']

    co_one = ['cool','coach','coat','coal','count','coin','coarse','coup','coif','cook','coign','coiffe','coof','court']
    co_two = ['coapt','coed','coinci']

    pre_one = ['preach']

    syls = 0 #added syllable number
    disc = 0 #discarded syllable number

    #1) if letters < 3 : return 1
    if len(word) <= 3 :
        syls = 1
        return syls

    #2) if doesn't end with "ted" or "tes" or "ses" or "ied" or "ies", discard "es" and "ed" at the end.
    # if it has only 1 vowel or 1 set of consecutive vowels, discard. (like "speed", "fled" etc.)

    if word[-2:] == "es" or word[-2:] == "ed" :
        doubleAndtripple_1 = len(re.findall(r'[eaoui][eaoui]',word))
        if doubleAndtripple_1 > 1 or len(re.findall(r'[eaoui][^eaoui]',word)) > 1 :
            if word[-3:] == "ted" or word[-3:] == "tes" or word[-3:] == "ses" or word[-3:] == "ied" or word[-3:] == "ies" :
                pass
            else :
                disc+=1

    #3) discard trailing "e", except where ending is "le"

    le_except = ['whole','mobile','pole','male','female','hale','pale','tale','sale','aisle','whale','while']

    if word[-1:] == "e" :
        if word[-2:] == "le" and word not in le_except :
            pass

        else :
            disc+=1

    #4) check if consecutive vowels exists, triplets or pairs, count them as one.

    doubleAndtripple = len(re.findall(r'[eaoui][eaoui]',word))
    tripple = len(re.findall(r'[eaoui][eaoui][eaoui]',word))
    disc+=doubleAndtripple + tripple

    #5) count remaining vowels in word.
    numVowels = len(re.findall(r'[eaoui]',word))

    #6) add one if starts with "mc"
    if word[:2] == "mc" :
        syls+=1

    #7) add one if ends with "y" but is not surrouned by vowel
    if word[-1:] == "y" and word[-2] not in "aeoui" :
        syls +=1

    #8) add one if "y" is surrounded by non-vowels and is not in the last word.

    for i,j in enumerate(word) :
        if j == "y" :
            if (i != 0) and (i != len(word)-1) :
                if word[i-1] not in "aeoui" and word[i+1] not in "aeoui" :
                    syls+=1

    #9) if starts with "tri-" or "bi-" and is followed by a vowel, add one.

    if word[:3] == "tri" and word[3] in "aeoui" :
        syls+=1

    if word[:2] == "bi" and word[2] in "aeoui" :
        syls+=1

    #10) if ends with "-ian", should be counted as two syllables, except for "-tian" and "-cian"

    if word[-3:] == "ian" :
    #and (word[-4:] != "cian" or word[-4:] != "tian") :
        if word[-4:] == "cian" or word[-4:] == "tian" :
            pass
        else :
            syls+=1

    #11) if starts with "co-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

    if word[:2] == "co" and word[2] in 'eaoui' :

        if word[:4] in co_two or word[:5] in co_two or word[:6] in co_two :
            syls+=1
        elif word[:4] in co_one or word[:5] in co_one or word[:6] in co_one :
            pass
        else :
            syls+=1

    #12) if starts with "pre-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

    if word[:3] == "pre" and word[3] in 'eaoui' :
        if word[:6] in pre_one :
            pass
        else :
            syls+=1

    #13) check for "-n't" and cross match with dictionary to add syllable.

    negative = ["doesn't", "isn't", "shouldn't", "couldn't","wouldn't"]

    if word[-3:] == "n't" :
        if word in negative :
            syls+=1
        else :
            pass

    #14) Handling the exceptional words.

    if word in exception_del :
        disc+=1

    if word in exception_add :
        syls+=1

    # calculate the output
    return numVowels - disc + syls
