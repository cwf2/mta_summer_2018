#!/usr/bin/env python3
''' Perform PCA on TF-IDF scores imported from type-scenes-jdmdh
'''

#
# import statements
#

import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text

from sklearn import decomposition
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
        description='Create samples from the corpus; plot.'
    )
    parser.add_argument('source',
        help='CSV file to import')
    parser.add_argument('--labels',
        help='Text file containing sample labels')
    parser.add_argument('--noninteractive',
        action = 'store_const', const=True, default=False,
        help="don't try to display results interactively")

    args = parser.parse_args()

    #
    # import data
    #

    print('Importing TF-IDF weights from {}'.format(args.source))
    m = np.loadtxt(args.source,
        delimiter = ',',
        encoding = 'utf-8',
        skiprows = 1,
        dtype = float)
    label = 'rtfidf'

    if args.labels is not None:
        print('Importing labels from {}'.format(args.labels))
        labels = np.loadtxt(args.labels, dtype=str)
    else:
        print('No sample labels provided.')
        labels = np.full(len(m), 'unknown')

    # cludge to fix graph title
    args.size = '-'

    # everything below is identical to sample.py

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
        output_file = 'plot_{}.pdf'.format(label)
        print('Saving plot to {}'.format(output_file))
        fig.savefig(output_file)
    else:
        fig.show()
