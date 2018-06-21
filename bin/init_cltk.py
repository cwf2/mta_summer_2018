#!/usr/bin/env python3
'''Download latin models for cltk'''

#
# import statements
#

import os

from cltk.stem.latin.j_v import JVReplacer
from cltk.tokenize.word import WordTokenizer
from cltk.stem.lemma import LemmaReplacer
from cltk.corpus.utils.importer import CorpusImporter


def runTest(text):
   '''Test cltk tools for latin'''
   print('Test phrase: ' + text)
   print()

   print('[1/3] Testing JVReplacer')
   jv = JVReplacer()
   text = jv.replace(text)
   print(' -> ' + text)
   print()

   print('[2/3] Testing WordTokenizer')
   tokenizer = WordTokenizer('latin')
   tok = tokenizer.tokenize(text)
   print(' -> ' + ', '.join(["'{}'".format(t) for t in tok]))
   print()

   print('[3/3] Testing LemmaReplacer')
   lemmatizer = LemmaReplacer('latin')
   lem = lemmatizer.lemmatize(tok)
   print(' -> ' + ', '.join(["'{}'".format(l) for l in lem]))
   print()


print('Testing Latin models for CLTK')

text = 'Jam lucis orto sidere, ' + \
       'Deum precemur supplices, ' + \
       'ut in diurnis actibus ' + \
       'nos servet a nocentibus.'

try:
    runTest(text)
except FileNotFoundError:
    print("Couldn't find models. Attempting to import them.")

    importer = CorpusImporter('latin')
    importer.import_corpus('latin_models_cltk')
    
    try:
        runTest(text)    
    except:
        print('FAIL: Could not install Latin models!')
        raise
except:
    print('FAIL: Unrecoverable error!')
    raise

print('Success!')

