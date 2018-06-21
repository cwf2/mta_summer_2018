#!/usr/bin/env python3
''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import json
import re

from mta_summer_2018 import Config, Text

from cltk.stem.latin.j_v import JVReplacer
from cltk.tokenize.word import WordTokenizer
from cltk.stem.lemma import LemmaReplacer


class Lem1(object):
    '''First version of CLTK lemmatizer'''

    def __init__(self):
        self.jv_replacer = JVReplacer()
        self.word_tokenizer = WordTokenizer('latin')
        self.lemmatizer = LemmaReplacer('latin')
        self.RE_PURGE = re.compile(r'[^a-z0-9\-]')
    
    def lemmatize(self, text):
        ortho = self.jv_replacer.replace(text.lower())
        tokens = self.word_tokenizer.tokenize(ortho)
        tokens = [tok for tok in tokens if re.search('[a-z]', tok)]
        lemmata = []
        for lem in self.lemmatizer.lemmatize(tokens):
            lem = re.sub(self.RE_PURGE, '', lem)
            if len(lem) > 0:
                lemmata.append(lem)

        return lemmata


class Lem2(object):
    '''First version of CLTK lemmatizer'''

    def __init__(self):
        self.jv_replacer = JVReplacer()
        self.word_tokenizer = WordTokenizer('latin')
        self.lemmatizer = LemmaReplacer('latin')
        self.RE_PURGE = re.compile(r'[^a-z0-9\-]')
    
    def lemmatize(self, text):
        ortho = self.jv_replacer.replace(text.lower())
        tokens = self.word_tokenizer.tokenize(ortho)
        tokens = [tok for tok in tokens if re.search('[a-z]', tok)]
        lemmata = []
        for lem in self.lemmatizer.lemmatize(tokens):
            lem = re.sub(self.RE_PURGE, '', lem)
            if len(lem) > 0:
                lemmata.append(lem)

        return lemmata
 
        
def lemmatizeText(text, lemmatizer):
    '''Read lines from JSON, return lemmata'''
    return [lemmatizer.lemmatize(l) for l in text.lines]


# main
if __name__ == '__main__':
    # Read the corpus metadata
    with open(Config.INDEX) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    
    l1 = Lem1()
    
    # Read the JSON files
    for text in corpus:
        text.dataFromJson(os.path.join(Config.DATA, 'corpus', text.author + '.json'))

        print('lemmatizing {}'.format(text.author))
        lemmata = lemmatizeText(text, l1)
        
        filename = os.path.join(Config.DATA, 'lemmata', text.author + '_lem.json')
        print('saving {}'.format(filename))
        with open(filename, 'w') as f:
            json.dump(list(zip(text.loci, lemmata)), f, indent=1)
