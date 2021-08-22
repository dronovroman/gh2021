# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 16:49:33 2021

@author: roman
"""
#########
# can pre-defined data categories used in variety of ABS surveys to monitor topics of importance 
# and test them as hypotheses in our topic modelling data worklow 
# applied to parliamentary data streams across all parliaments
#########

from flask import Flask
import os
import threading
import atexit
import logging

####
threshold = 0.85 # this value will later be included into configuration file
abs_loc = ''
####

topic_daemon_url  = 'http://127.0.0.1:5004/' # in prod this will be a part of global config

import json
import requests
from transformers import pipeline
import json, os
import requests

file_path=''
app = Flask(__name__)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# get ABS covid19 survey categories from ABS API
URL = 'https://api.data.abs.gov.au/data/ABS,COVID_SALTS?&format=jsondata'
data = requests.get(URL)
dataset = json.loads(data.text)
dataset['data']['structure']['dimensions']['series']
abs_survey_categories = [i['name'] for i in dataset['data']['structure']['dimensions']['series'][3]['values']]
abs_covid_hypotheses = list(set(['Due to coronavirus '+i.replace('in the last 4 weeks', '').split('-')[0].strip().lower() for i in abs_survey_categories]))
print(abs_covid_hypotheses)

# ABS_IT_BARRIER  # Barriers to general business activities or performance
URL = 'https://api.data.abs.gov.au/data/ABS,ABS_IT_BARRIER?&format=jsondata'
data = requests.get(URL)
dataset = json.loads(data.text)
dataset['data']['structure']['dimensions']['series'][0]
abs_survey_categories = [i['name'] for i in dataset['data']['structure']['dimensions']['series'][0]['values']]
abs_barriers_hypotheses = list(set([i.split('-')[0].strip() + ' is a barrier to business activity' for i in abs_survey_categories]))
print(abs_barriers_hypotheses)
# we can take these and other topics and include them as level 2 topics under relevant level1 category.

def get_high_prob_items(res_c, threshold):
    sl = dict()
    d = dict(zip(res_c['labels'], res_c['scores']))
    for k in d.keys():
        if d[k] > threshold:
            sl[k]=d[k]
    return sl

@app.route('/<path:filename>', methods=['GET', 'POST']) 
def index(filename):
    global model, tokenizer, filepath, _path, classifier, abs_covid_hypotheses, abs_barriers_hypotheses
    _path = os.path.abspath(str(filename))
    _path = _path.replace('//','/')
    if _path[-4:]!='.wav':
        print('Processing ',str(_path))
        #print('file not supported')
        return "file not supported"
    else:
        print('Processing ',str(_path))
        filepath = _path
        t_transcribe5 = threading.Thread(name='ABS surveys topic modelling daemon', target=det_ABS_topicCall)
        t_transcribe5.setDaemon(True)
        t_transcribe5.start()
    return 'ABS Surveys topic modelling thread has been started...'




def det_ABS_topicCall():
    global model, tokenizer, filepath, _path, classifier, abs_covid_hypotheses, abs_barriers_hypotheses
    logging.debug('Starting topic thread...')
    # loc of our wav file
    abs_loc = os.path.abspath(_path)    
    #f=_path # may need fixing
    with open(abs_loc.replace('.wav','.json'), 'r') as jsf:
        metad = json.load(jsf)
    premise = metad['transcription']

    # test ABS covid survey statement hypotheses
    res_c = classifier(premise, abs_covid_hypotheses, multi_label=True)
    returns = get_high_prob_items(res_c, threshold)         ##############
    metad['abs_covid_categories'] = list(returns.keys())
    print('ABS covid survey topics: ', returns)
    
    # test ABS barriers to business survey statement hypotheses
    res_c = classifier(premise, abs_barriers_hypotheses, multi_label=True)
    returns = get_high_prob_items(res_c, threshold)
    metad['abs_barriers_to_business'] = list(returns.keys())
    print('ABS business impediments survey topics: ', returns)
    # write data back to object
    with open(abs_loc.replace('.wav','.json'), 'w') as jsf:
        json.dump(metad, jsf, indent=2)

    logging.debug('Completed topic determination...')
    # here we can call another service daemon if we meed to, and pass the file location in abs_loc
    _ = requests.get(topic_daemon_url + abs_loc)

# cleaning
def close_threads():
    """
    stops all running daemon threads at exit
    """    
    global t_transcribe5    
    try:
        t_transcribe5.cancel()
        print('Closed topic thread...')
    except:
        print('Could not close topic thread...')  
    
    
atexit.register(close_threads)
if __name__ == '__main__':
  app.run(host='127.0.0.1', port = 5003)








    
    
    
    