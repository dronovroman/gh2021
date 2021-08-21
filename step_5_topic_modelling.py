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
file_path=''
app = Flask(__name__)

#reusing the transcription app to spin out a topic determination service as a daemon




@app.route('/<path:filename>', methods=['GET', 'POST']) 
def index(filename):
    global model, tokenizer, filepath, _path
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




def det_topicCall():
    global model, tokenizer, filepath, _path
    logging.debug('Starting topic thread...')
    f=_path # may need fixing

  
    logging.debug('Completed topic determination...')


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