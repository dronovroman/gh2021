# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 12:49:26 2021

@author: roman
"""


from flask import Flask
import os
import threading
import atexit
import logging

# path for debugging
#pth = 'E:\\gh2021\\raw_data\\eedd150a524d388e5f8bd8bfbd81770b34197a8e57f41fa987507ee3ee5f2e8d\\2021-08-21-11-05-16.wav'
threshold = 0.8 # using a rather high confidence threshold for topic cut-off

from transformers import pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
import json
#reusing the transcription app to spin out a topic determination service as a daemon


# getting topics
with open(os.path.relpath('./res/topics.json'), 'r') as jsf:
    topics = json.load(jsf)

file_path=''
app = Flask(__name__)

@app.route('/<path:filename>', methods=['GET', 'POST']) 
def index(filename):
    global model, tokenizer, filepath, _path, topics, classifier
    _path = os.path.abspath(str(filename))
    _path = _path.replace('//','/')
    if _path[-4:]!='.wav':
        print('Processing ',str(_path))
        #print('file not supported')
        return "file not supported"
    else:
        print('Processing ',str(_path))
        filepath = _path
        t_transcribe = threading.Thread(name='speaker determination daemon', target=det_topicCall)
        t_transcribe.setDaemon(True)
        t_transcribe.start()
    return 'Topics thread has been started...'


#### helper functions

def get_l2_labels(topics):
    tpc = []
    for t1 in topics.values():
        for t in t1:
            tpc.append(t)
    return list(set(tpc))

def get_l1_basedon_l2(topics, l2): #l2 is a list of l2 topics
    ll = []
    for l in l2:
        return_key = ""
        for key in topics.keys():
            if l in topics[key]:
                return_key = key
        ll.append(return_key)
    return ll

def get_high_prob_items(res_c, threshold):
    sl = dict()
    d = dict(zip(res_c['labels'], res_c['scores']))
    for k in d.keys():
        if d[k] > threshold:
            sl[k]=d[k]
    return sl



def det_topicCall():
    global model, tokenizer, filepath, _path, topics, classifier
    logging.debug('Starting topic thread...')
    # loc of our wav file
    abs_loc = os.path.abspath(_path)
    
    #f=_path # may need fixing
    with open(abs_loc.replace('.wav','.json'), 'r') as jsf:
        metad = json.load(jsf)
    premise = metad['transcription']
    
    res_c = classifier(premise, get_l2_labels(topics), multi_label=True)  
    
    l2 = get_high_prob_items(res_c, threshold)
    
    l1 = get_l1_basedon_l2(topics, list(l2.keys()))    
    metad['l1_topics'] = l1
    metad['l2_topics'] = list(l2.keys())
    print(l1, l2)
    with open(abs_loc.replace('.wav','.json'), 'w') as jsf:
        json.dump(metad, jsf, indent=2)
    logging.debug('Completed topic determination...')
    # here we can call another service daemon if we meed to, and pass the file location in abs_loc


# cleaning
def close_threads():
    """
    stops all running daemon threads at exit
    """    
    global t_transcribe    
    try:
        t_transcribe.cancel()
        print('Closed topic thread...')
    except:
        print('Could not close topic thread...')  
    
    
    
atexit.register(close_threads)
if __name__ == '__main__':
  app.run(host='127.0.0.1', port = 5003)