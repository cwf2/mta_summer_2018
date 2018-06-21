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

from collections import Counter
import gensim
from sklearn import decomposition

#
# functions
#

def sample(lines, sample_size, offset=0):
    '''group lines in to paragraphs'''
    # TODO
    samples = []
    working = []

    for i, line in enumerate(lines):
        working += line
        if (i+1-offset) % sample_size == 0:
            samples.append(working)
            working = []
    if len(working) > 0:
        samples.append(working)

    return samples


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


def loadLemmata(text):
    '''load lemmata from json file'''

    filename = os.path.join(Config.DATA, 'lemmata',
        text.author + '_' + args.lemfile + '.json')

    with open(filename) as f:
        data = json.load(f)
        text.lemmata = [lems for loc, lems in data]

def calcWordFreqs(samples):
    '''Calculate corpus-wide token frequencies'''

    frequency = defaultdict(int)
    for text in samples:
        for token in text:
            frequency[token] += 1

    return frequency

#
# main
#

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Load lemmata, create samples'
    )
    parser.add_argument('--size',
        type=int, default=30,
        help='sample size (lines)')
    parser.add_argument('--offset',
        type=int, default=0,
        help='window offset (lines)')
    parser.add_argument('--label',
        type=str, default=None,
        help='series label')
    parser.add_argument('--lemfile',
        type=str, default='lem',
        help='lemma file suffix')

    args = parser.parse_args()

    # Read the corpus metadata
    with open(Config.INDEX) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]

    # initialize samples
    samples = []
    labels = []

    # read the corpus data
    for text in corpus:

        # load lines
        # text.dataFromJson(
        #    os.path.join(Config.DATA, 'corpus', text.author + '.json'))

        # generate lemmata
        loadLemmata(text)

        # sample
        s = sample(text.lemmata, args.size, args.offset)
        samples.extend(s)
        labels.extend([text.author] * len(s))

    # calculate corpus-wide word frequencies
    freq = Counter([tok for sample in samples for tok in sample])

    # remove hapax legomena
    samples = [
        [token for token in sample if freq[token] > 1]
            for sample in samples]

	 # delete small samples
    # TODO

    # create gensim dictionary
    dictionary = gensim.corpora.Dictionary(samples)
    dict_file = os.path.join(Config.DATA, 'gensim', args.lemfile + '.dict')
    dictionary.save(dict_file)

    # create vector model
    vec = [dictionary.doc2bow(sample) for sample in samples]

    # tfidf weighting
    # TODO

    # convert gensim vectors to numpy matrix
    m = gensim.matutils.corpus2dense(vec, num_terms=len(dictionary))
    m = m.transpose()

    # pca
    npcs = 10
    pcmodel = decomposition.PCA(npcs)
    pca = pcmodel.fit_transform(m)

    # plot
    # FIXME in progress ...
    import numpy as np
    from matplotlib import pyplot

    labels = np.array(labels)
    fig = pyplot.figure(figsize=(8,5))
    ax = fig.add_axes([.1,.1,.6,.8])
    ax.set_title('Samples of {} lines'.format(args.size))
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')
    for i, l in enumerate(set(labels)):
        ax.plot(pca[labels==l,0], pca[labels==l,1], ls='', marker='o',
            color='C'+str(i), label=l)
    fig.legend()
    fig.show()
