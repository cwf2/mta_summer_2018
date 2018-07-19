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
# functions
#


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
    ax.set_title(args.title)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # plot each author as a separate series
    for i, auth in enumerate(sorted(set(authors))):
        ax.plot(pca[authors==auth,0], pca[authors==auth,1], ls='', marker='o',
            color=colors[i], label=auth)

    # add legend
    fig.legend()

    # write output
    if args.out is None:
        file_out = '{}.{}'.format(args.series, args.format)
    else:
        file_out = args.out
        if not (file_out.endswith('.pdf') or file_out.endswith('.png')):
            file_out += '.' + args.format

    print('Saving plot to {}'.format(file_out))
    fig.savefig(file_out)
