#!/usr/bin/env python3
''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import json
import argparse
import numpy as np

from mta_summer_2018 import Config, Text

#
# functions
#

def sample(lines, sample_size, offset=0):
    '''group lines in to paragraphs'''
    
    samples = np.split(lines, np.arange(offset, lines.size, sample_size))
    return [' '.join(s) for s in samples]

#
# main
#

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Populate corpus from remote CTS server'
    )
    parser.add_argument('--server', 
        metavar='URL', type=str, default=Config.SERVER_URL,
        help='remote CTS server')
    parser.add_argument('--index', 
        metavar="FILE", default=Config.INDEX_PATH,
        help='corpus index file')
    parser.add_argument('--dest', 
        metavar="DIR", default=Config.LOCAL_BASE,
        help='local corpus directory')

    args = parser.parse_args()

    # Read the corpus metadata
    with open(args.index) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
        
    # Read the JSON files
    for text in corpus:
        text.dataFromJson(os.path.join(args.dest, text.author + '.json'))
        
        print('{} {}: {} lines'.format(text.author, text.title, len(text.lines)))
        
        s = sample(text.lines, 50)
        
        print('--> {} samples'.format(len(s)))
        print()
        