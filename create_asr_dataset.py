# -*- coding: utf-8 -*-
"""
Created on Fri Aug 20 23:48:48 2021

@author: roman
"""

#Dataset prep for ASR - using Hugginface datasets

import tarfile
import glob 
import os
import pandas as pd
from scipy.io import wavfile
import scipy.signal as sps
import librosa    
import time

os.chdir('E:\\gh2021\\asr_data')
all_files = glob.glob("data\\*\\*\\*", recursive=False) 
##########################
#make sure wav sample rate is 16000
new_rate = 16000
for f in all_files:
    if '.wav' in f:
        #print(f)
        # check wav file for sr
        sampling_rate, data = wavfile.read(f)
        #resample only if sr != 16k
        if True: # sampling_rate != 16000:
            y, s = librosa.load(f, sr=16000) # Downsample 44.1kHz to 8kHz
            print('fixing sample rate for ', f)
            wavfile.write(f, new_rate, y)
    # 
    if '.txt' in f:
        # read text
        with open(f, 'r') as reader:
            f_content = reader.read()
        f_content = f_content.upper()
        time.sleep(0.01)
        # write 
        with open(f, 'w') as writer:
            writer.write(f_content)

##########################







