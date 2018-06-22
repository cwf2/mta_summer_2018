''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import sys
import json
import argparse

from collections import Counter
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text

#
# functions
#

def sampleMaker(text, sampleSize, offset):
    
    count = 0
    chunk = []
    book = []
    
    for verse in text[:]:
        count = count + 1
        chunk.extend(verse)
        if count % sampleSize == offset:
            book.append(chunk)
            chunk = []
            
    return book

#
# main
#

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='create samples from the corpus'
    )
    parser.add_argument('--size', 
        metavar='N', type=int, default=30,
        help='sample size in lines')
    parser.add_argument('--offset', 
        metavar="N", default = 0,
        help='offset in lines')
    

    args = parser.parse_args()
    
    
    # Read the corpus metadata
    with open(Config.INDEX_PATH) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    counts = Counter()    
    # Read the JSON files
    samples = []
    labels = []
    for text in corpus:
        
        filename = os.path.join(Config.LOCAL_BASE, text.author + '_lem.json')
        with open(filename) as f:
            lemmatized = json.load(f)
        sams = sampleMaker(lemmatized, args.size, args.offset )
        labels.extend([text.author] * len(sams))
        samples.extend(sams)
        
"""Created on Fri Jun 22 13:45:33 2018

@author: Alex
"""

