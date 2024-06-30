# Quick script to edit TH17.5's music for looping, fading, etc,
# like you would in Touhou Music Room.

# To use, be sure to install ffmpeg and have the ffmpeg binaries
# on your PATH. Then, use something like thcrap with datdump
# enabled in the configuration to dump all the files. Navigate
# to data/bgm, put this script in that folder, and invoke it with
# python with your desired settings.

# Feel free to change LOOP_COUNT, FADE_DURATION, and FADE_ALGO as
# you see fit. The resulting output will be wav files.

LOOP_COUNT = 2     # Must be 1 or greater
FADE_DURATION = 10 # In seconds
FADE_ALGO = "exp"  # See https://ffmpeg.org/ffmpeg-filters.html#afade-1 under "curve" for fade algorithm options


import os
import subprocess
from pathlib import Path

files = [f for f in os.listdir(os.getcwd()) if os.path.isfile(f)]

for f in files:
    if not f.endswith(".ogg"):
        continue

    fpath = os.path.join(os.getcwd(), f)
    inifile = os.path.join(os.getcwd(), f) + ".ini"
    outfile = os.path.join(os.getcwd(), Path(f).stem) + ".wav"

    rs = None
    re = None
    try:
        with open(inifile) as ini:
            lines = ini.readlines()
            for l in lines:
                if l.startswith("repeatstart="):
                    rs = l.split("=")[-1].strip()
                if l.startswith("repeatend="):
                    re = l.split("=")[-1].strip()
    except:
        subprocess.run(f"ffmpeg -y -i \"{fpath}\" \"{outfile}\"", shell=True)
        continue

    if rs is None or re is None:
        subprocess.run(f"ffmpeg -y -i \"{fpath}\" \"{outfile}\"", shell=True)
        continue

    lo = LOOP_COUNT - 1
    subprocess.run(f"ffmpeg -y -i \"{fpath}\" "
                     + f"-filter_complex \" "
                         + f"[0:a] atrim=start_sample=0:end_sample={rs}, asetpts=PTS-STARTPTS [a]; "
                         + f"[0:a] atrim=start_sample={rs}:end_sample={re}, asetpts=PTS-STARTPTS, aloop={lo}:size={re}-{rs} [b]; "
                         + f"[0:a] atrim=start_sample={rs}:end_sample={FADE_DURATION}*44100+{rs}, asetpts=PTS-STARTPTS, afade=t=out:curve={FADE_ALGO}:nb_samples={FADE_DURATION}*44100 [c]; "
                         + f"[a] [b] [c] concat=n=3:v=0:a=1 [outa]\" "
                     + f"-map \"[outa]\" "
                     + f"\"{outfile}\"", shell=True)
