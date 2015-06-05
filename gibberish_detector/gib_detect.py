#!/usr/bin/python

import pickle
import sys
import re
def check(text):
    tokens=re.findall("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+",text)
    if len(tokens)==0:
        return None
    is_gibberishes=[]
    for token in tokens:
        with open('pypg.config','r') as config:
            path=config.read()
            sys.path.append(path)
        from gibberish_detector import gib_detect_train
        model_data = pickle.load(open(path.strip()+'gibberish_detector/gib_model.pki', 'rb'))
        l=token
        model_mat = model_data['mat']
        threshold = model_data['thresh']
        tp=gib_detect_train.avg_transition_prob(l, model_mat)
        print('threshold ' + str(threshold))
        if not tp  > threshold:
            is_gibberishes.append({'token':token,'tp':tp})
            print (token+" >>>")
    if len(tokens) is None or len(is_gibberishes)/len(tokens) < 0.5:
        return None
    else:
        return is_gibberishes
