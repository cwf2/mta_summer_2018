#!/usr/bin/env python3
''' Plot feature vectors
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
        description='Plot feature vectors'
    )
    parser.add_argument('series',
        help='Sample series to plot.')
    parser.add_argument('--title',
        metavar='TITLE', type=str, default=None,
        help='Title for graph. Defaults to "SERIES".')
    parser.add_argument('--out',
        metavar='FILE', type=str, default=None,
        help='Output file name. Defaults to "plot_SERIES.pdf".')
    parser.add_argument('--format',
        metavar='FMT', type=str, default='pdf', choices=['pdf', 'png'],
        help='Output file format.')

    args = parser.parse_args()

    # set default title
    if args.title is None:
        args.title = args.series

    # check that data exists
    cache = os.path.join(Config.DATA, 'cache', args.series)
    if not os.path.exists(cache):
        print("Can't find series {}".format(args.series))
        exit(1)

    #
    # load data
    #

    # data paths
    file_loci = os.path.join(cache, 'loci.txt')
    file_authors = os.path.join(cache, 'authors.txt')
    file_pca = os.path.join(cache, 'pca.txt')

    # load author labels
    print('Reading {}'.format(file_authors))
    authors = np.loadtxt(file_authors, dtype=str)

    # load loci
    print('Reading {}'.format(file_loci))
    with open(file_loci) as f:
      loci = json.load(f)
      firstlines = [l[0] for l in loci]

    # load pca
    print('Reading {}'.format(file_pca))
    pca = np.loadtxt(file_pca)

    #
    # Plot
    #

    print('Plotting')

    # create figure, canvas
    fig = basePlot(xs=pca[:,0], ys=pca[:,1],
        labels=authors, colors=COLORS, title=args.title)

    # write output
    if args.out is None:
        file_out = '{}.{}'.format(args.series, args.format)
    else:
        file_out = args.out
        if not (file_out.endswith('.pdf') or file_out.endswith('.png')):
            file_out += '.' + args.format

    print('Saving plot to {}'.format(file_out))
    fig.savefig(file_out)
