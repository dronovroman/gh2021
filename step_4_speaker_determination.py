# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:56:23 2021

@author: roman
"""


######################
# use a set threshold for speaker recognition
threshold = 0.38
######################


from flask import Flask
import os
import threading
file_path=''
app = Flask(__name__)

#reusing the transcription app to spin out a speaker determination service as a daemon

#Admin priveliges are required to run speechbrain
from speechbrain.pretrained import SpeakerRecognition
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="res/pretrained_models/spkrec-ecapa-voxceleb")

import glob 
import os
import json
import atexit
import logging
import pandas as pd


all_wav = glob.glob("./res/voiceprints/*.wav", recursive=False)
speakers = dict()
for spf in all_wav:
    name = str(spf).split("\\")[-1][:-4]
    speakers[name]= os.path.abspath(spf)
#speakers contains voiceprints

verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="res/pretrained_models/spkrec-ecapa-voxceleb")

@app.route('/<path:filename>', methods=['GET', 'POST']) 
def index(filename):
    global model, tokenizer, filepath, t_transcribe, speakers, verification, _path, threshold
    _path = os.path.abspath(str(filename))
    _path = _path.replace('//','/')
    if _path[-4:]!='.wav':
        print('Processing ',str(_path))
        #print('file not supported')
        return "file not supported"
    else:
        print('Processing ',str(_path))
        filepath = _path
        t_transcribe = threading.Thread(name='speaker determination daemon', target=det_speakerCall)
        t_transcribe.setDaemon(True)
        t_transcribe.start()
    return 'Speaker tread has been started...'




def det_speakerCall():
    global model, tokenizer, filepath, t_transcribe, speakers, verification, _path, threshold
    logging.debug('Starting speaker thread...')
    f=_path # may need fixing
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
  
    logging.debug('Completed speaker determination...')


# cleaning
def close_threads():
    """
    stops all running daemon threads at exit
    """    
    global t_transcribe    
    try:
        t_transcribe.cancel()
        print('Closed transcription thread...')
    except:
        print('Could not close transcription thread...')  
    
    
    
atexit.register(close_threads)
if __name__ == '__main__':
  app.run(host='127.0.0.1', port = 5002)



