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


####
threshold = 0.8 # this value will later be included into configuration file
abs_loc = ''
####

import json
import requests
from transformers import pipeline
import json, os
import requests

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

with open(abs_loc.replace('.wav','.json'), 'r') as jsf:
    metad = json.load(jsf)

premise = metad['transcription']

def get_high_prob_items(res_c, threshold):
    sl = dict()
    d = dict(zip(res_c['labels'], res_c['scores']))
    for k in d.keys():
        if d[k] > threshold:
            sl[k]=d[k]
    return sl
# test ABS covid survey statement hypotheses
res_c = classifier(premise, abs_covid_hypotheses, multi_label=True)
returns = get_high_prob_items(res_c, threshold)         ##############
metad['abs_covid_categories'] = list(returns.keys())

# test ABS barriers to business survey statement hypotheses
res_c = classifier(premise, abs_barriers_hypotheses, multi_label=True)
returns = get_high_prob_items(res_c, threshold)
metad['abs_barriers_to_business'] = list(returns.keys())


# write data back to object
with open(abs_loc.replace('.wav','.json'), 'w') as jsf:
       json.dump(metad, jsf, indent=2)
    
    
    
    