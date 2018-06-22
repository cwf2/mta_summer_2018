#!/usr/bin/env python3
''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import json

from collections import Counter

from mta_summer_2018 import Config, Text

from cltk.stem.latin.j_v import JVReplacer
from cltk.tokenize.word import WordTokenizer
from cltk.stem.lemma import LemmaReplacer

#
# functions
#

def whiteTok(tok):
    
    whiteList = ['a', 'b', 'c', 'd','e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 
                 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', 
                 '3', '4', '5', '6', '7', '8', '9', '0', '-']
    
    chars = [c for c in tok if c in whiteList]
    token = ''.join(chars)
    
    if len(token) > 0:
        return token

def lemmanade(lines):
    
    count = 0
    #chunk = ''
    #tokenBook = []
    lemons = []
    #hapaxLegomena = []
    jvReplace = JVReplacer()
    wordTokenizer = WordTokenizer('latin')
    lemmatizer = LemmaReplacer('latin')
    
    
    
    for verse in lines:
        
        count = count + 1
       # chunk = chunk + verse
        
        chunkLow = jvReplace.replace(verse.lower())
        
        #tokenize the words
        chunkTok = wordTokenizer.tokenize(chunkLow)
        chunkTok = [whiteTok(tok) for tok in chunkTok if whiteTok(tok) is not None]
        #lemmatize the tokens
        lemmata = lemmatizer.lemmatize(chunkTok)
        
        #add lno and lemmata to a list and clear the chunk
        #tokenBook.append([lno, lemmata])
        #chunk = ''
        
        #add all the lemmatized tokens together in a string
        lemons.append(lemmata)
            
        
    #return tokenBook
    return lemons

#
# main
#

if __name__ == '__main__':
    
    countFile = 'wordCounts.tsv'
    
    # Read the corpus metadata
    with open(Config.INDEX_PATH) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
        
    # Read the JSON files
    for text in corpus:
        text.dataFromJson(os.path.join(Config.LOCAL_BASE, text.author + '.json'))
        
        lemmatized = lemmanade(text.lines)
        counts = Counter([lem for line in lemmatized for lem in line])
        with open(countFile, 'w') as f:
        
            for word,count in counts.most_common():
                line = word + '\t' + str(count) + '\n'
                f.write(line)
            
            #if number in counts > 1:
                #hapaxLegomena.append([word, count])
            
    