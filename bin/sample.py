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

def sampleMaker(lines, sample_size, offset):
    '''Create samples of consecutive lines'''

    count = 0
    chunk = []
    book = []

    for line in lines:
        count = count + 1
        chunk.extend(line)
        if count % sample_size == offset:
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

    # clean cache dir
    cache = os.path.join(Config.DATA, 'cache', args.label)
    if not os.path.exists(cache):
        os.makedirs(cache)

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
    loci = []
    authors = []

    # iterate over texts
    for text in corpus:
        print(' - {} {}'.format(text.author, text.title), end='...')
        text.dataFromJson(os.path.join(Config.DATA, 'lines', text.author + '.json'))

        # read feature file, sample
        filename = os.path.join(Config.DATA, args.feature, text.author + '.json')
        with open(filename) as f:
            features = json.load(f)
        sams = sampleMaker(features, args.size, args.offset)
        locs = sampleMaker([[l] for l in text.loci], args.size, args.offset)
        print('{} samples'.format(len(sams)))

        # add these samples, labels to master lists
        authors.extend([text.author] * len(sams))
        loci.extend(locs)
        samples.extend(sams)

    # save author labels
    authors = np.array(authors)
    author_file = os.path.join(cache, 'authors.txt')
    print('Writing {}'.format(author_file))
    np.savetxt(author_file, authors, fmt='%s')

    # save loci
    loci_file = os.path.join(cache, 'loci.txt')
    print('Writing {}'.format(loci_file))
    with open(loci_file, 'w') as f:
        json.dump(loci, f)

    #
    # feature extraction
    #

    # load gensim dictionary
    dict_file = os.path.join(Config.DATA, args.feature, 'gensim.dict')
    dictionary = gensim.corpora.Dictionary.load(dict_file)

    # create vector model
    print('Building vector model')
    vec = [dictionary.doc2bow(sample) for sample in samples]

    # tfidf weighting
    tfidf_model = gensim.models.TfidfModel(vec)
    tfidf = tfidf_model[vec]

    # convert gensim vectors to numpy matrix
    m = gensim.matutils.corpus2dense(tfidf, num_terms=len(dictionary))
    m = m.transpose()

    # save TF-IDF features
    tfidf_file = os.path.join(cache, 'tfidf.txt')
    print('Writing {}'.format(tfidf_file))
    np.savetxt(m, tfidf_file)

    #
    # dimensionality reduction
    #

    # PCA
    npcs = 10
    print('Calculating {} principal components'.format(npcs))
    pcmodel = decomposition.PCA(npcs)
    pca = pcmodel.fit_transform(m)

    # save PCA features
    pca_file = os.path.join(cache, 'pca.txt')
    np.savetxt(pca_file, pca)

    #
    # output
    #

    print('Plotting')

    # try to simulate R Color Brewer's Set 1
    colors = [
        '#ff0000', # red
        '#0000dd', # blue
        '#00dd00', # green
        '#8800aa', # purple
        '#ff8800', # orange
        '#eeee00', # yellow
    ]

    # create figure, canvas
    fig = pyplot.figure(figsize=(8,5))
    ax = fig.add_axes([.1,.1,.6,.8])
    ax.set_title(args.label)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # plot each author as a separate series
    for i, auth in enumerate(sorted(set(authors))):
        ax.plot(pca[authors==auth,0], pca[authors==auth,1], ls='', marker='o',
            color=colors[i], label=auth)

    # add legend
    fig.legend()

    # if noninteractive, default to pdf output
    if args.noninteractive:
        output_file = 'plot_{}.png'.format(args.label)
        print('Saving plot to {}'.format(output_file))
        fig.savefig(output_file)
    else:
        fig.show()
