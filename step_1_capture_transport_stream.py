# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 6:53:10 2021

@author: roman
"""

import json
import time
import requests
import os
from moviepy import editor
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from browsermobproxy import Server
import sys
from datetime import datetime, timedelta
import hashlib
import json


url ="https://parlview.aph.gov.au/mediaPlayer.php?videoID=551585&operation_mode=parlview"

folder = str(hashlib.sha256(url.encode()).hexdigest())

try:
    os.mkdir('raw_data\\'+ folder)
    print(folder, ' created...')
except:
    print('could not create folder ', folder)

transcription_daemon_url='http://127.0.0.1:5001/'

#start proxy server
server = Server("res\\browsermob-proxy\\bin\\browsermob-proxy.bat")
server.start()
proxy = server.create_proxy()
options = webdriver.ChromeOptions()
# options.add_argument('headless')
options.add_argument("--window-size=1920,1080");
options.add_argument("--proxy-server={0}".format(proxy.proxy))
caps = DesiredCapabilities.CHROME.copy()
caps['acceptSslCerts'] = True
caps['acceptInsecureCerts'] = True
ref_handle = "twitch"
proxy.new_har(ref_handle, options={'captureHeaders': True,'captureContent':True,'captureBinaryContent': True})
driver = webdriver.Chrome('chromedriver',options=options,desired_capabilities=caps)
driver.get(url)

time.sleep(3)
driver.find_element_by_css_selector('[class="switch-image"]').click()


filename = ""
data=None

initial_data = True
fetched = []
global_end = False
def parse_har():
    #global filename, fetched, data
    found_nothing_new = True
    global fetched, initial_data, global_end, filename
    filename = datetime.now().strftime("raw_data\\"+folder+"\\%Y-%m-%d-%H-%M-%S")+'.mpeg' 
    for ent in proxy.har['log']['entries']:
        _url = ent['request']['url']
        _response = ent['response']
        #make sure havent already downloaded this piece
        if _url in fetched:
            continue
        if _url.endswith('.ts'):
            found_nothing_new = False
            if not initial_data:
                #check if this url had a valid response, if not, ignore it
                if 'text' not in _response['content'].keys() or not _response['content']['text']:
                    continue
                print(_url+'\n')
                r1 = requests.get(_url, stream=True)
                if(r1.status_code == 200 or r1.status_code == 206):
        
                    # re-open output file to append new video
                    with open(filename,'ab') as f:
                        data = b''
                        for chunk in r1.iter_content(chunk_size=1024):
                            if(chunk):
                                data += chunk
                        f.write(data)
                        fetched.append(_url)
                else:
                    print("Received unexpected status code {}".format(r1.status_code))   
            initial_data=False
            fetched.append(_url)
    if found_nothing_new:
        global_end = True



        try:
            clip = editor.AudioFileClip(filename)
            clip.write_audiofile(filename.replace('mpeg', 'wav'),fps = 16000, codec='pcm_s16le')
            print('converted to audio...')
        except:
            print('could not convert to audio...')
            pass
        try:
            #os.remove(filename)
            pass
        except:
            pass # remove mpeg data to keep only wav
    
metad = dict()
def update_meta():
    global metad, counter,start_timestamp
    counter += 1
    metad['source_url'] = url
    metad['folder'] = folder
    metad['_datetime'] = str(datetime.now())
    metad['event_start'] = ''
    metad['time_offset'] = str(datetime.now() - start_timestamp)
    metad['sequence_nr'] = counter
    metad['speakers'] = ''
    metad['transcription'] = ''
    metad['l1_topics'] = ''
    metad['l2_topics'] = ''
    metad['restored_transcript'] = ''
    metad['alignment_to_datasets'] = str(dict())
    



init_time = datetime.now()
start_timestamp = datetime.now()
counter = 0
print('initialised at: ', str(init_time))

#for zz in range(130)
while not global_end:
    time.sleep(1)
    if init_time + timedelta(seconds = 57) <= datetime.now()  :
        if filename != "": # try convert and delete
            print('file: ', filename)
            try:
                clip = editor.AudioFileClip(filename)
                clip.write_audiofile(filename.replace('mpeg', 'wav'),fps = 16000, codec='pcm_s16le')
                with open(filename.replace('.mpeg','.json'), 'w') as jsf:
                    json.dump(metad, jsf, indent=2)
                # after conversion - we call a transcription daemon
                time.sleep(.1)
                abs_loc = str(os.path.abspath(filename.replace('mpeg', 'wav')))
                r = requests.get(transcription_daemon_url+abs_loc)
                print('converted to audio...')
            except:
                print('could not convert to audio...')
                pass
            try:
                os.remove(filename)
                print(filename, ' was removed')
                pass
            except:
                print('could not remove ', filename)
                pass # remove mpeg data to keep only wav
        init_time = datetime.now()
        parse_har()
        update_meta()
        print('new_chunk_started')




#########################

server.stop()
driver.quit()


###





