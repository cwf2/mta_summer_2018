#!/usr/bin/env python3
''' Create a set of evenly-sized samples from the corpus
'''

#
# import statements
#

import os
import sys
import json
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text

import gensim
from sklearn import decomposition
import numpy as np

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
        description='Create samples from the corpus; plot.'
    )
    parser.add_argument('--size',
        metavar='N', type=int, default=30,
        help='sample size in lines')
    parser.add_argument('--offset',
        metavar="N", default = 0,
        help='offset in lines')
    parser.add_argument('--feature',
        metavar="NAME", default = 'lemmata',
        help='featureset to sample from')
    parser.add_argument('--noninteractive',
        action = 'store_const', const=True, default=False,
        help="don't try to display results interactively")


    args = parser.parse_args()


    #
    # sampling
    #

    print('Sampling {}: size={}; offset={}'.format(args.feature, args.size, args.offset))

    # Read the corpus metadata
    with open(Config.INDEX) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    
    # initialize corpus-wide samples, labels
    samples = []
    labels = []

    # iterate over texts
    for text in corpus:
        print(' - {} {}'.format(text.author, text.title), end='...')

        # read feature file, sample
        filename = os.path.join(Config.DATA, args.feature, text.author + '.json')
        with open(filename) as f:
            features = json.load(f)
        sams = sampleMaker(features, args.size, args.offset )
        print('{} samples'.format(len(sams)))
        
        # add these samples, labels to master lists
        labels.extend([text.author] * len(sams))
        samples.extend(sams)

    # load gensim dictionary
    dict_file = os.path.join(Config.DATA, args.feature, 'gensim.dict')
    dictionary = gensim.corpora.Dictionary.load(dict_file)

    #
    # transformations
    #

    # create vector model
    print('Building vector model')
    vec = [dictionary.doc2bow(sample) for sample in samples]

    # tfidf weighting
    # TODO

    #
    # dimensionality reduction
    #

    # convert gensim vectors to numpy matrix
    m = gensim.matutils.corpus2dense(vec, num_terms=len(dictionary))
    m = m.transpose()

    # pca
    npcs = 10
    pcmodel = decomposition.PCA(npcs)
    pca = pcmodel.fit_transform(m)

    #
    # output
    #

    # if noninteractive, default to pdf output
    if args.noninteractive:
        import matplotlib
        matplotlib.use('PDF')
        output_file = 'plot.{} {} {}.pdf'.format(args.feature, args.size, args.offset)
    from matplotlib import pyplot

    # plot
    # FIXME : in progress ...

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
    
    if args.noninteractive:
        fig.savefig(output_file)
    else:
        fig.show()
