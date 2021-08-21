# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:10:50 2021

@author: roman
"""


from flask import Flask 
import os
import threading
from transformers import Wav2Vec2Tokenizer, Wav2Vec2ForCTC
import torch
import os
import librosa
import json
import atexit
import logging
import requests


# transcription daemon should call the speaker determination daemon once it finishes processing data...
speker_daemon_url='http://127.0.0.1:5002/' # speaker deemon is now configured on this port


### folder_path = "E:\\project\\raw_data\\eedd150a524d388e5f8bd8bfbd81770b34197a8e57f41fa987507ee3ee5f2e8d"

tokenizer = Wav2Vec2Tokenizer.from_pretrained("res\\models\\wav2vec2-aph-cap")
model = Wav2Vec2ForCTC.from_pretrained("res\\models\\wav2vec2-aph-cap\\checkpoint-3000")
file_path=''

# wrap code into a minimum flask app and spin out threads for async processing
app = Flask(__name__)
    
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
        t_transcribe = threading.Thread(name='trancription daemon', target=transcribeCall)
        t_transcribe.setDaemon(True)
        t_transcribe.start()
    return 'Transcription tread has been started...'



def transcribeCall():
    logging.debug('Starting transcription thread...')
    global model, tokenizer, filepath
    _path = filepath
    metad = dict()
    abs_loc = os.path.abspath(_path)
    with open(_path.replace('.wav','.json'), 'r') as jsf:
        metad = json.load(jsf)
    # metad['transcription'] contains transcription
    y, sr = librosa.load(_path)
    hlf = int(len(y)/2)
    yy = [y[:hlf], y[hlf:] ] # splitting audio in half due to very high resource demand for 60 sec
    transcr = ""
    for prt in yy:    
        input_values = tokenizer(prt, return_tensors="pt", padding="longest").input_values 
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.batch_decode(predicted_ids)
        [tts] = transcription
        transcr = transcr + " " + tts
    both_parts = transcr.lower()
    metad['transcription'] = both_parts
    with open(_path.replace('.wav','.json'), 'w') as jsf:
        json.dump(metad, jsf, indent=2)
    print(str(both_parts)+'\n')
    logging.debug('Completed transcription...')
    print('Trying to call the speaker determination daemon...')
    _ = requests.get(speker_daemon_url + abs_loc)


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
  app.run(host='127.0.0.1', port = 5001)
  
  
  
  


