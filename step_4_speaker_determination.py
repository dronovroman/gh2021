# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:56:23 2021

@author: roman
"""


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

all_wav = glob.glob("./res/voiceprints/*.wav", recursive=False)
speakers = dict()
for spf in all_wav:
    name = str(spf).split("\\")[-1][:-4]
    speakers[name]= os.path.abspath(spf)
#speakers contains voiceprints



@app.route('/<path:filename>', methods=['GET', 'POST']) 
def index(filename):
    global model, tokenizer, filepath, t_transcribe
    _path = os.path.abspath(str(filename))
    _path = _path.replace('//','/')
    if _path[-4:]!='.wav':
        print('Processing ',str(_path))
        #print('file not supported')
        return "file not supported"
    else:
        print('Processing ',str(_path))
        filepath = _path
        t_transcribe = threading.Thread(name='trancription daemon', target=det_speakerCall)
        t_transcribe.setDaemon(True)
        t_transcribe.start()
    return 'Transcription tread has been started...'




def det_speakerCall():
    logging.debug('Starting transcription thread...')
  
    logging.debug('Completed transcription...')


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



