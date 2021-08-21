# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:10:50 2021

@author: roman
"""


from transformers import Wav2Vec2Tokenizer, Wav2Vec2ForCTC
from datasets import load_dataset
import soundfile as sf
import torch
import os, glob
import librosa
import soundfile as sf
import json

tokenizer = Wav2Vec2Tokenizer.from_pretrained("res\\models\\wav2vec2-aph-cap")
model = Wav2Vec2ForCTC.from_pretrained("res\\models\\wav2vec2-aph-cap\checkpoint-1500")


folder_path = "E:\\project\\raw_data\\eedd150a524d388e5f8bd8bfbd81770b34197a8e57f41fa987507ee3ee5f2e8d"



file_list = os.listdir(folder_path)
lstWav = [f for f in file_list if f.endswith('.wav')]
tts_str = ""
for f in lstWav:
    _path = _path = os.path.abspath(folder_path +'\\'+f)
    metad = dict()
    with open(_path.replace('.wav','.json'), 'r') as jsf:
        metad = json.load(jsf)
    # metad['transcription'] contains transcription
    y, sr = librosa.load(_path)
    hlf = int(len(y)/2) 
    yy = [y[:hlf], y[hlf:] ]
    transcr = ""
    for prt in yy:    
        input_values = tokenizer(prt, return_tensors="pt", padding="longest").input_values 
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.batch_decode(predicted_ids)
        [tts] = transcription
        transcr = transcr + " " + tts
    both_parts = transcr.lower()
    tts_str = tts_str + " " + both_parts
    metad['transcription'] = both_parts
    with open(_path.replace('.wav','.json'), 'w') as jsf:
        json.dump(metad, jsf, indent=2)
    print(str(both_parts)+'\n')







