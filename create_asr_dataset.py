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


#train
train_files = glob.glob("data\\train\\*\\*", recursive=False) 
l = []
i=0
for f in train_files:
    d = dict()
    i+=1
    d['index'] = i
    d['test_or_train'] = 'TRAIN'
    d['filename'] = f.split('\\')[-1]
    d['path_from_data_dir'] = str(f)[5:].replace('\\','/')
    d['path_from_data_dir_windows'] = str(f)[5:].replace('\\','\\\\')
    if '.wav' in str(f).lower():
        d['is_converted_audio'] = 'FALSE'
        d['is_audio'] = 'TRUE'
        d['is_word_file'] = 'FALSE'
        d['is_phonetic_file'] = 'FALSE'
        d['is_sentence_file'] = 'FALSE'
    else:
        d['is_converted_audio'] = 'FALSE'
        d['is_audio'] = 'FALSE'
        d['is_word_file'] = 'FALSE'
        d['is_phonetic_file'] = 'FALSE'
        d['is_sentence_file'] = 'TRUE'

    l.append(d)
df = pd.DataFrame(l)
df.to_csv('train_data.csv', mode = 'w', index=False)


#train
test_files = glob.glob("data\\test\\*\\*", recursive=False) 

l = []
i=0
for f in test_files:
    d = dict()
    i+=1
    d['index'] = i
    d['test_or_train'] = 'TEST'
    d['filename'] = f.split('\\')[-1]
    d['path_from_data_dir'] = str(f)[5:].replace('\\','/')
    d['path_from_data_dir_windows'] = str(f)[5:].replace('\\','\\\\')
    if '.wav' in str(f).lower():
        d['is_converted_audio'] = 'FALSE'
        d['is_audio'] = 'TRUE'
        d['is_word_file'] = 'FALSE'
        d['is_phonetic_file'] = 'FALSE'
        d['is_sentence_file'] = 'FALSE'
    else:
        d['is_converted_audio'] = 'FALSE'
        d['is_audio'] = 'FALSE'
        d['is_word_file'] = 'FALSE'
        d['is_phonetic_file'] = 'FALSE'
        d['is_sentence_file'] = 'TRUE'

    l.append(d)
df = pd.DataFrame(l)
df.to_csv('test_data.csv', mode = 'w', index=False)
time.sleep(1)
all_files = glob.glob("*", recursive=False) 
a = tarfile.open('asr_data.tar', 'w')
for f in all_files:
    if '.py' not in str(f):
        a.add(f)
    
a.close()


### show transcriptions\
    
os.chdir('E:\\gh2021\\asr_data')
all_files = glob.glob("data\\*\\*\\*", recursive=False) 
for f in all_files:
    if '.txt' in str(f).lower():
        print(f, ' : ')
        with open(f, "r") as op: #, encoding="utf-8"
                transcript = op.read()
                print(transcript)





