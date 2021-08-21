# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 16:49:33 2021

@author: roman
"""
#########
# can pre-defined data categories used in variety of ABS surveys to monitor topics of importance 
# and test them as hypotheses in our topic modelling data worklow 
# applied to parliamentary data streams across all parliaments


import json
import requests
URL = 'https://api.data.abs.gov.au/data/ABS,COVID_SALTS?&format=jsondata'
data = requests.get(URL)
dataset = json.loads(data.text)
dataset['data']['structure']['dimensions']['series']
abs_survey_categories = [i['name'] for i in dataset['data']['structure']['dimensions']['series'][3]['values']]
abs_covid_hypotheses = list(set(['Due to coronavirus '+i.replace('in the last 4 weeks', '').split('-')[0].strip().lower() for i in abs_survey_categories]))
print(abs_covid_hypotheses)


#ABS_IT_BARRIER  # Barriers to general business activities or performance
URL = 'https://api.data.abs.gov.au/data/ABS,ABS_IT_BARRIER?&format=jsondata'
data = requests.get(URL)
dataset = json.loads(data.text)
dataset['data']['structure']['dimensions']['series'][0]
abs_survey_categories = [i['name'] for i in dataset['data']['structure']['dimensions']['series'][0]['values']]
abs_sc_clean = list(set([i.replace('in the last 4 weeks', '').split('-')[0].strip() for i in abs_survey_categories]))
print(abs_sc_clean)
# we can take these and other topics and include them as level 2 topics under relevant level1 category.
