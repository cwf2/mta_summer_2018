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

import matplotlib
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
        description='Divide features into even-sized samples and plot.'
    )
    parser.add_argument('--size',
        metavar='SIZE', type=int, default=30,
        help='Make samples of SIZE lines. Default 30.')
    parser.add_argument('--offset',
        metavar='OFFSET', type=int, default = 0,
        help='Shift samples by OFFSET lines. Default 0.')
    parser.add_argument('--feature',
        metavar='FEAT', type=str, default = 'lemmata',
        help='Featureset to sample. Default "lemmata".')
    parser.add_argument('--label',
        metavar='LABEL', type=str, default=None,
        help='Trial label (for graph). Default "FEAT-SIZE-OFFSET"')
    parser.add_argument('--noninteractive',
        action = 'store_const', const=True, default=False,
        help="Don't try to display results interactively.")


    args = parser.parse_args()

    if args.label is None:
        args.label = '{f}-{s}-{o}'.format(
            f = args.feature,
            s = args.size,
            o = args.offset)

    #
    # sampling
    #

    print('Sampling {f}: size={s}; offset={o}'.format(
        f = args.feature,
        s = args.size,
        o = args.offset))

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
    tfidf_model = gensim.models.TfidfModel(vec)
    tfidf = tfidf_model[vec]

    # convert gensim vectors to numpy matrix
    m = gensim.matutils.corpus2dense(tfidf, num_terms=len(dictionary))
    m = m.transpose()

    #
    # dimensionality reduction
    #

    # pca
    npcs = 10
    print('Calculating {} principal components'.format(npcs))
    pcmodel = decomposition.PCA(npcs)
    pca = pcmodel.fit_transform(m)

    #
    # output
    #

    print('Plotting')
    labels = np.array(labels)

    # create figure, canvas
    fig = pyplot.figure(figsize=(8,5))
    ax = fig.add_axes([.1,.1,.6,.8])
    ax.set_title('Samples of {} lines'.format(args.size))
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # plot each author as a separate series
    for i, l in enumerate(sorted(set(labels))):
        ax.plot(pca[labels==l,0], pca[labels==l,1], ls='', marker='o',
            color='C'+str(i), label=l)

    # add legend
    fig.legend()

    # if noninteractive, default to pdf output
    if args.noninteractive:
        output_file = 'plot_{}.pdf'.format(args.label)
        print('Saving plot to {}'.format(output_file))
        fig.savefig(output_file)
    else:
        fig.show()
