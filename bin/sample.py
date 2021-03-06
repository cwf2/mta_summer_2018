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

def sampleMaker(lines, size, step, offset):
    '''Create samples of consecutive lines'''

    samples = []

    for start in range(offset, len(lines)-size, step):
        this_sample = []
        for l in lines[start:(start+size)]:
            this_sample.extend(l)
        samples.append(this_sample)

    return samples

#
# main
#

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Create samples from the corpus, either in contiguous chunks (default) or using a sliding window.'
    )
    parser.add_argument('--size',
        metavar='SIZE', type=int, default=30,
        help='Make samples of SIZE lines. Default 30.')
    parser.add_argument('--offset',
        metavar='OFFSET', type=int, default = 0,
        help='Shift samples by OFFSET lines. Default 0.')
    parser.add_argument('--step',
        metavar='STEP', type=int, default = None,
        help='Move window by STEP lines each time. Default SIZE (no overlap between samples).')
    parser.add_argument('--feature',
        metavar='FEAT', type=str, default = 'lemmata',
        help='Featureset to sample. Default "lemmata".')
    parser.add_argument('--label',
        metavar='LABEL', type=str, default=None,
        help='Trial label. Default "FEAT-SIZE-OFFSET"')

    args = parser.parse_args()

    # set the default series label
    if args.label is None:
        if args.step is None:
            args.label = '{f}-{s}-{o:02d}'.format(
                f = args.feature,
                s = args.size,
                o = args.offset)
        else:
            args.label = '{f}-{s}-{t}-{o:02d}'.format(
                f = args.feature,
                s = args.size,
                t = args.step,
                o = args.offset)
            
    # set the default step size
    if args.step is None:
        args.step = args.size

    # clean cache dir
    cache = os.path.join(Config.DATA, 'cache', args.label)
    if not os.path.exists(cache):
        os.makedirs(cache)

    #
    # sampling
    #

    print('Sampling {f}: size={s}; step={t}; offset={o}'.format(
        f = args.feature,
        s = args.size,
        t = args.step,
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
        sams = sampleMaker(features, args.size, args.step, args.offset)
        locs = sampleMaker([[l] for l in text.loci], args.size, args.step, args.offset)
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
    np.savetxt(tfidf_file, m)

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