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

import gensim
from sklearn import decomposition
import numpy as np
from matplotlib import pyplot

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

    # create gensim dictionary
    dictionary = gensim.corpora.Dictionary(samples)
    #dict_file = os.path.join(Config.DATA, 'gensim', args.lemfile + '.dict')
    #dictionary.save(dict_file)

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
