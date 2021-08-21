# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:56:23 2021

@author: roman
"""




#######################
threshold = 0.38
pth = '\\raw_data\\eedd150a524d388e5f8bd8bfbd81770b34197a8e57f41fa987507ee3ee5f2e8d\\2021-08-21-11-05-16.wav'
#########################

#Admin priveliges are required to run this code
from speechbrain.pretrained import SpeakerRecognition
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="res/pretrained_models/spkrec-ecapa-voxceleb")

import pandas as pd
import glob 
import os
import json

all_wav = glob.glob("./res/voiceprints/*.wav", recursive=False)
speakers = dict()
for spf in all_wav:
    name = str(spf).split("\\")[-1][:-4]
    speakers[name]= os.path.abspath(spf)
#speakers contains voiceprints


f=pth # may need fixing
l = []
dr = dict()
for s in speakers.keys():
    d=dict()            
    score, prediction = verification.verify_files(speakers[s], f)    
    d['speaker'] = s
    d['score'] = score.numpy()[0]
    l.append(d)    
df = pd.DataFrame(l)
likely_speaker = df[df['score']==df['score'].max()][['speaker']].iloc[0,0]
likely_speaker_score = df['score'].max()
if likely_speaker_score < threshold:
    likely_speaker = 'Unknown'
ls_dict=dict() # in case we need a dictionary
ls_dict[likely_speaker] = df['score'].max()
print(str(f).split("\\")[-1], likely_speaker, likely_speaker_score)
with open(f.replace('.wav','.json'), 'r') as jsf:
    metad = json.load(jsf)
metad['speakers']=likely_speaker
with open(f.replace('.wav','.json'), 'w') as jsf:
        json.dump(metad, jsf, indent=2)



