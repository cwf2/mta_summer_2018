#!/usr/bin/env python3
''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import sys
import json
import shutil
from collections import Counter

from cltk.stem.latin.j_v import JVReplacer
from cltk.tokenize.word import WordTokenizer
from cltk.stem.lemma import LemmaReplacer

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text

#
# functions
#

def whiteTok(tok, whitelist='abcdefghijklmnopqrstuvwxyz01234567890-'):
    '''scrub non-whitelisted characters'''

    chars = [c for c in tok if c in whitelist]
    token = ''.join(chars)
    
    if len(token) > 0:
        return token


def lemmanade(lines):
    
    count = 0
    lemons = []

    # initialize cltk tools
    jvReplace = JVReplacer()
    wordTokenizer = WordTokenizer('latin')
    lemmatizer = LemmaReplacer('latin')
        
    for verse in lines:
        
        count = count + 1
        
        # lowercase
        verse = jvReplace.replace(verse.lower())
        
        #tokenize the words
        chunkTok = wordTokenizer.tokenize(verse)
        chunkTok = [whiteTok(tok) for tok in chunkTok if whiteTok(tok) is not None]

        #lemmatize the tokens
        lemmata = lemmatizer.lemmatize(chunkTok)
                
        #add all the lemmatized tokens together in a string
        lemons.append(lemmata)
    
    return lemons

#
# main
#

if __name__ == '__main__':
    # paths
    source = os.path.join(Config.DATA, 'lines')
    dest = os.path.join(Config.DATA, 'lemmata')
    count_file = os.path.join(Config.DATA, 'wordCounts.tsv')

    print("Cleaning lemma directory {}".format(dest))

    # clean destination directory
    if os.path.exists(dest):
        shutil.rmtree(dest)
        os.makedirs(dest)
    else:
        os.makedirs(dest)
    
    # Read the corpus metadata
    with open(Config.INDEX) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]

    # initialize word counts
    counts = Counter()
    
    print("Lemmatizing...")
    
    # Read the JSON files
    for text in corpus:
        print(" - {} {}".format(text.author, text.title))
        
        text.dataFromJson(os.path.join(source, text.urn + '.json'))
        
        # tokenize and lemmatize
        lemmatized = lemmanade(text.lines)
        
        # save lemmata
        filename = os.path.join(dest, text.urn + '.json')
        with open(filename, 'w') as f:
            json.dump(lemmatized, f)
            
        # update word counts
        counts.update([lem for line in lemmatized for lem in line])
        
    # write word counts
    print('Writing word counts to ' + count_file)
    
    with open(count_file, 'w') as f:
    
        for word,count in counts.most_common():
            line = word + '\t' + str(count) + '\n'
            f.write(line)
    