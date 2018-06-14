#!/usr/bin/env python3
''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import json
import argparse

from mta_summer_2018 import Config, Text

#
# functions
#

def sample(lines, sample_size, offset=0):
    '''group lines in to paragraphs'''
    # TODO
    pass

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
        
        # TODO : call sample
        samples = sample(text.lines, sample_size=50)