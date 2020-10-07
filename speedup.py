import argparse
from speedup_functions import *

parser = argparse.ArgumentParser(description="Speed up podcast differently for each speaker")

# Basic parameters
parser.add_argument("-f", "--filename", type=str, dest="filename", help="Path of the sound file you want to speed up",
                    required=True)
parser.add_argument("-n", "--n_speakers", type=int, dest="n_speakers", help="Number of people speaking (0 if unkown)",
                    default=0)
parser.add_argument("-s", "--speeds", nargs='+', type=float, dest="speeds", help="Speed of each speaker in the extract")
parser.add_argument("-save", "--save-file", type=str, dest="save_file", help="Path of the file we want to save to",
                    default=None)

# More options
parser.add_argument('--show-speakers', dest="show_speakers",
                    help="Whether to play an extract of each speaker before asking for the speeds", action='store_true')
parser.set_defaults(show_speakers=False)
parser.add_argument("-auto", "--automatic", dest="auto",
                    help="Whether to automatically match the speeds of the two speakers (EXPERIMENTAL)",
                    action='store_true')
parser.set_defaults(auto=False)

# Technical arguments for diarization
# FAST
parser.add_argument("--chunk-size", type=float, dest="chunk_size", help="Size of each chunk during speaker diarization",
                    default=1.0)
parser.add_argument("--short-window", type=float, dest="short_window", help="", default=0.2)
parser.add_argument("--mid-window", type=float, dest="mid_window", help="", default=4.0)
parser.add_argument("--lda-dim", type=int, dest="lda_dim", help="", default=35)
# SLOW
# parser.add_argument("--chunk-size", type=float, dest="chunk_size", help="Size of each chunk during speaker diarization", default=0.1)
# parser.add_argument("--short-window", type=float, dest="short_window", help="", default=0.05)
# parser.add_argument("--mid-window", type=float, dest="mid_window", help="", default=2.0)
# parser.add_argument("--lda-dim", type=int, dest="lda_dim", help="", default=35)

# Argument for debugging
#parser.add_argument("--save-diarization", type = bool)

args = parser.parse_args()
pipeline(args)

