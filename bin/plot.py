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
    '#eedd00', # yellow
    '#00dd00', # green
    '#8800aa', # purple
    '#ff8800', # orange
    '#0000dd', # blue
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
FIG_W = 12
FIG_H = 7

#
# functions
#

def basePlot(xs, ys, labels, colors=COLORS, title=None, legend=False):
    '''Basic plot'''

    # if we're going to have a legend, adjust figure width to make room
    if legend and len(set(labels)) > 1:
       w = .6
    else:
       w = .8

    # create figure, canvas
    fig = pyplot.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([.1, .1, w, .8])
    if title is not None:
        ax.set_title(title)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # marker set to use
    markers = 'ovP*Xd^43p'

    # plot each author as a separate series
    for i, l in enumerate(sorted(set(labels))):
        ax.plot(xs[labels==l], ys[labels==l],
            ls='', marker=markers[i], color=colors[i], label=l)

    # add legend
    if legend and len(set(labels)) > 1:
        fig.legend()

    return fig

def ACAbasePlot(xs, ys, labels, colors=COLORS, title=None, legend=False, hi=None):
    '''Basic plot w/ single author highlighted'''

    # if we're going to have a legend, adjust figure width to make room
    if legend and len(set(labels)) > 1:
       w = .6
    else:
       w = .8

    # create figure, canvas
    fig = pyplot.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([.1, .1, w, .8])
    if title is not None:
        ax.set_title(title)
    ax.set_xlabel('PC1')
    ax.set_ylabel('PC2')

    # marker set to use
    markers = 'ovP*Xd^43p'
    
    i_hi = None
    l_hi = None

    # plot each author as a separate series
    for i, l in enumerate(sorted(set(labels))):
        if l == hi:
            color = colors[i]
            i_hi = i
            l_hi = l
        else:
            color = '#aaaaaa'
        ax.plot(xs[labels==l], ys[labels==l],
            ls='', marker=markers[i], color=color, label=l)

    if i_hi is not None:
        ax.plot(xs[labels==l_hi], ys[labels==l_hi],
            ls='', marker=markers[i_hi], color=colors[i_hi])

    # add legend
    if legend and len(set(labels)) > 1:
        fig.legend()

    return fig

class Trial(object):
    '''Represents one sample set'''

    def __init__(self, label):
        if self._checkCache(label):
            self._loadSampleLabels()
            self._loadPCA()


    def _checkCache(self, label):
        '''load data from cache'''

        # locate the cached data, check series label exists
        cache = os.path.join(Config.DATA, 'cache', label)
        if os.path.exists(cache):
            self.PATH = cache
            self.LABEL = label
            return True
        else:
            print("Can't find trial {}".format(label))
            return False


    def _loadSampleLabels(self):
        '''load authors, loci'''

        # load the author labels
        file_authors = os.path.join(self.PATH, 'authors.txt')
        print('Reading {}'.format(file_authors))
        self.authors = np.loadtxt(file_authors, dtype=str)

        # load the loci
        file_loci = os.path.join(self.PATH, 'loci.txt')
        print('Reading {}'.format(file_loci))
        with open(file_loci) as f:
          self.loci = json.load(f)
          self.firstlines = np.array([l[0] for l in self.loci])


    def _loadPCA(self):
        '''load pca feature set'''

        file_pca = os.path.join(self.PATH, 'pca.txt')
        print('Reading {}'.format(file_pca))
        self.pca = np.loadtxt(file_pca)


    def findLoc(self, auth, loc, quiet=False):
        '''Return sample index containing given locus'''

        in_auth = np.arange(len(self.authors))[self.authors==auth]

        for i in in_auth:
            if loc in self.loci[i]:
                return i

        if not quiet:
            print("Couldn't find {} {}".format(auth, loc))


    def findLocWithin(self, auth, loc, lim, quiet=False):
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
            i = self.findLoc(auth, '{}.{}'.format(bk, l), quiet=True)
            if i is not None:
                if not quiet:
                    print(' -> using {}.{}'.format(bk, l))
                return i


    def findPassage(self, auth, loc_start, loc_stop):
        '''Return all sample indices in a range of loci'''

        i_start = self.findLoc(auth, loc_start)
        i_stop = self.findLoc(auth, loc_stop)
        if i_stop is None:
            i_stop = self.findLocWithin(auth, loc_stop, 0)

        if (i_start is not None) and (i_stop is not None):
            i_start, i_stop = sorted([i_start, i_stop])
            return range(i_start, i_stop+1)


    def plotAuthor(self, auth, marker='', points=SHADOW[0], corpus=False,
                   text='#000000'):
        '''plot one author'''
        
        # generate title
        title = '{} : {}'.format(self.LABEL, auth)

        # background image
        if corpus:
            # plot shadow version of larger dataset
            mask = self.authors != auth
            fig = basePlot(xs=self.pca[mask, 0], ys=self.pca[mask, 1],
                    labels=self.authors[mask], colors=SHADOW, title=title)
            ax = fig.get_axes()[0]
        else:
            # create figure, canvas
            fig = pyplot.figure(figsize=(FIG_W, FIG_H))
            ax = fig.add_axes([.1,.1,.8,.8])
            ax.set_title(title)
            ax.set_xlabel('PC1')
            ax.set_ylabel('PC2')

        # select data by author name
        xs = self.pca[self.authors==auth, 0]
        ys = self.pca[self.authors==auth, 1]
        tags = self.firstlines[self.authors==auth]

        # plot, but with no points
        ax.plot(xs, ys, ls='', marker = marker, color=points)

        # add locus tags at every x,y point
        if text is not None:
            for x, y, tag in zip(xs, ys, tags):
                ax.text(x, y, tag, fontsize=6, color=text)

        return fig


    def plotTestPassages(self, filename, title=None):
        '''Read in a list of passages and plot them'''

        authors = []
        passages = []
        tags = []

        if title is None:
            title = filename

        with open(filename) as f:
            for l in f:
                auth, loc_start, loc_stop, tag = l.strip().split()
                s_id = self.findPassage(auth, loc_start, loc_stop)
                authors.append(auth)
                passages.extend(s_id)
                tags.extend([tag] * len(s_id))

        # plot shadow version of larger dataset
        mask = np.isin(self.authors, authors)
        fig = basePlot(xs=self.pca[mask, 0], ys=self.pca[mask, 1],
                labels=self.authors[mask], colors=SHADOW, title=title)

        # select data by sample id
        xs = self.pca[passages, 0]
        ys = self.pca[passages, 1]

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


    def tracePassage(self, author, loc_start, loc_stop, anim=False):
        '''Follow relative movement of sample across a scene'''

        fig = self.plotAuthor(author, marker='o', points=SHADOW[-1], text=None)
        ax = fig.get_axes()[0]
        ax.set_title('{} {}-{}'.format(author, loc_start, loc_stop))
        ids = self.findPassage(author, loc_start, loc_stop)

        if anim:
            text_colour = "#e0e0e0"
        else:
            text_colour = "#000000"

        for i in ids:
            ax.text(self.pca[i, 0], self.pca[i, 1], self.firstlines[i], fontsize=6,
                    color=text_colour)

        lab = ax.text(self.pca[i, 0], self.pca[i, 1], self.firstlines[i], fontsize=6)

        if anim:
            from matplotlib.animation import FuncAnimation

            def update(i):
                lab.set_x(self.pca[i, 0])
                lab.set_y(self.pca[i, 1])
                lab.set_text(self.firstlines[i])

            fig = FuncAnimation(fig, update, frames=ids)

        return fig

#
# main
#

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Plot feature vectors'
    )
    parser.add_argument('trial',
        help='Name of the sample set to plot.')
    parser.add_argument('--title',
        metavar='TITLE', type=str, default=None,
        help='Title for graph. Defaults to "TRIAL".')
    parser.add_argument('--out',
        metavar='FILE', type=str, default=None,
        help='Output file name. Defaults to "plot/TRIAL.pdf".')
    parser.add_argument('--format',
        metavar='FMT', type=str, default='pdf', choices=['pdf', 'png'],
        help='Output file format.')

    args = parser.parse_args()

    # set default title
    if args.title is None:
        args.title = args.trial

    #
    # Load data
    #

    trial = Trial(args.trial)

    #
    # Plot
    #

    print('Plotting')

    # create figure, canvas
    fig = basePlot(xs=trial.pca[:,0], ys=trial.pca[:,1],
        labels=trial.authors, colors=COLORS, title=args.title)

    # write output
    if args.out is None:
        file_out = '{}.{}'.format(args.trial, args.format)
    else:
        file_out = args.out
        if not (file_out.endswith('.pdf') or file_out.endswith('.png')):
            file_out += '.' + args.format

    file_out = os.path.join('plot', file_out)

    print('Saving plot to {}'.format(file_out))
    fig.savefig(file_out)
