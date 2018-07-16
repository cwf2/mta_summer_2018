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
# global values
#

# try to simulate R Color Brewer's Set 1
COLORS = [
    '#ff0000', # red
    '#0000dd', # blue
    '#00dd00', # green
    '#8800aa', # purple
    '#ff8800', # orange
    '#eeee00', # yellow
]
# background version for type scene overlay
SHADOW = [
    '#aaaaaa', # red
    '#999999', # blue
    '#dddddd', # green
    '#888888', # purple
    '#bbbbbb', # orange
    '#eeeeee', # yellow    
]


#
# functions
#

def sampleMaker(lines, sample_size, offset):

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


def plotAuthor(auth):
    '''plot one author'''
        
    # create figure, canvas
    fig = pyplot.figure(figsize=(8,5))
    ax = fig.add_axes([.1,.1,.8,.8])
    ax.set_title('Python - {}'.format(auth))
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # select data by author name
    xs = pca[labels==auth, 0]
    ys = pca[labels==auth, 1]
    tags = [l[0] for l in loci[labels==auth]]

    # plot, but with no points
    ax.plot(xs, ys, ls='', marker = '')

    # add locus tags at every x,y point
    for x, y, tag in zip(xs, ys, tags):
        ax.text(x, y, tag, fontsize=6)

    return fig
    

def findLoc(auth, loc, quiet=False):
    '''Return sample index containing given locus'''
    
    in_auth = np.arange(len(labels))[labels==auth]
    
    for i in in_auth:
        if loc in loci[i]:
            return i
    
    if not quiet:
        print("Couldn't find {} {}".format(auth, loc))        


def findLocWithin(auth, loc, lim, quiet=False):
    '''Look for locus within a range'''
    
    bk, start = loc.split('.')
    start = int(start)
    if lim > start:
        step = 1
    elif lim < start:
        step = -1
    else:
        step = 1
        lim = start
    
    for l in range(start, lim, step):
        i = findLoc(auth, '{}.{}'.format(bk, l), quiet=True)
        if i is not None:
            if not quiet:
                print(' -> using {}.{}'.format(bk, l))
            return i


def findPassage(auth, loc_start, loc_stop):
    '''Return all sample indices in a range of loci'''
    
    i_start = findLoc(auth, loc_start)
    i_stop = findLoc(auth, loc_stop)
    if i_stop is None:
        i_stop = findLocWithin(auth, loc_stop, 0)            
            
    if (i_start is not None) and (i_stop is not None):
        i_start, i_stop = sorted([i_start, i_stop])
        return range(i_start, i_stop+1)
            


def basePlot(xs, ys, labels, colors, title):
    '''Basic plot'''
     
    # if we're going to have a legend, adjust figure width to make room
    if len(set(labels)) > 1:
        w = .6
    else:
        w = .8
    
    # create figure, canvas
    fig = pyplot.figure(figsize=(8,5))
    ax = fig.add_axes([.1, .1, w, .8])
    ax.set_title(title)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # marker set to use
    markers = 'ovP*4D^x3p'

    # plot each author as a separate series
    for i, l in enumerate(sorted(set(labels))):
        ax.plot(xs[labels==l], ys[labels==l], 
            ls='', marker=markers[i], color=colors[i], label=l)

    # add legend
    if len(set(labels)) > 1:
        fig.legend()
    
    return fig


def plotTestPassages(filename, title=None):
    '''Read in a list of passages and plot them'''
    
    authors = []
    passages = []
    tags = []
    
    if title is None:
        title = filename
    
    with open(filename) as f:
        for l in f:
            auth, loc_start, loc_stop, tag = l.strip().split()
            s_id = findPassage(auth, loc_start, loc_stop)
            authors.append(auth)
            passages.extend(s_id)
            tags.extend([tag] * len(s_id))

    # plot shadow version of larger dataset
    mask = np.isin(labels, authors)
    fig = basePlot(pca[mask, 0], pca[mask, 1], labels[mask], SHADOW, title)

    # select data by sample id
    xs = pca[passages, 0]
    ys = pca[passages, 1]

    # grab first axis in figure
    ax = fig.axes[0]
    
    # plot just the marked passages in color
    for i, t in enumerate(sorted(set(tags))):
        ax.plot(xs[tags==t], ys[tags==t], 
            ls='', marker='.', color=COLORS[i])

    # add locus tags at every x,y point
    for x, y, tag in zip(xs, ys, tags):
        ax.text(x, y, tag, fontsize=6)

    return fig

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
    loci = []

    # iterate over texts
    for text in corpus:
        print(' - {} {}'.format(text.author, text.title), end='...')
        text.dataFromJson(os.path.join(Config.DATA, 'lines', text.author + '.json'))

        # read feature file, sample
        filename = os.path.join(Config.DATA, args.feature, text.author + '.json')
        with open(filename) as f:
            features = json.load(f)
        sams = sampleMaker(features, args.size, args.offset )
        print('{} samples'.format(len(sams)))

        # add these samples, labels to master lists
        labels.extend([text.author] * len(sams))
        samples.extend(sams)
        
        # save the loci as well
        loci.extend(sampleMaker([[l] for l in text.loci], 
            args.size, args.offset))

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
    loci = np.array(loci)

    fig = basePlot(pca[:,0], pca[:,1], labels, COLORS, args.label)

    # if noninteractive, default to pdf output
    if args.noninteractive:
        output_file = 'plot_{}.png'.format(args.label)
        print('Saving plot to {}'.format(output_file))
        fig.savefig(output_file)
    else:
        fig.show()
        
    #
    # individual plots for all authors
    #
    
    for l in sorted(set(labels)):
        print('Drawing detailed plot for {}'.format(l))
        
        filename = os.path.join('plot', 'plot_py_{}.pdf'.format(l))
        fig = plotAuthor(auth=l)
        
        print('Writing {}'.format(filename))
        fig.savefig(filename)
