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

from cltk.stem.latin.j_v import JVReplacer
from cltk.tokenize.word import WordTokenizer
from cltk.stem.lemma import LemmaReplacer

#
# functions
#

def sample(lines, sample_size, offset=0):
    '''group lines in to paragraphs'''
    # TODO
    pass


def bind(text, samplesize = 30, offset = 0):
    '''stores lines in a list'''
    
    count = 0
    chunk = ''
    book = []
    
    for verse in text:
        count = count + 1
        chunk = chunk + verse
        if count % samplesize == offset:
            book.append(chunk)
            chunk = ''
    
    return book

def lemmatize(chunk):
    
    jvReplace = JVReplacer()
    chunkLow = jvReplace.replace(chunk.lower())
    
    wordTokenizer = WordTokenizer('latin')
    chunkTok = wordTokenizer.tokenize(chunkLow)
    chunkTok = [token for token in chunkTok if token not in ['.', ',', ':', ';']]
    chunkTok = [token for token in chunkTok if len(token) > 0]
    
    
    lemmatizer = LemmaReplacer('latin')
    lemmata = lemmatizer.lemmatize(chunkTok)
    
    #lemmatized.append(lemmata)
    
    return lemmata

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
    for text in corpus[:1]:
        text.dataFromJson(os.path.join(args.dest, text.author + '.json'))
        
        # TODO : call sample
        samples = bind(text.lines)
        lemmatized = []
        count = 0
        for sample in samples:
            count = count + 1
            lemmatized.append(lemmatize(sample))
            print(count, '/', len(samples))
            
        #samples = [lemmatize(sample) for sample in bind(text.lines)]
        
       
