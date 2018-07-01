#!/usr/bin/env python3
''' Modified from lemmatize.py
'''

#
# import statements
#

import os
import sys
import json
import shutil
import argparse
from collections import Counter

import numpy
import gensim

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text

#
# functions
#

def loadRData(file):
    '''Read in the samples exported from r'''

    with open(file) as f:
        records = json.load(f)

    labels = numpy.array([rec['auth'] for rec in records])
    all_features = numpy.array([rec['tok'] for rec in records])

    return labels, all_features

#
# main
#

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Load features from type-scenes-jdmdh export'
    )
    parser.add_argument('source',
        help='JSON file to import')
    parser.add_argument('--feature',
        metavar="NAME", default = 'rlemmata',
        help='Featureset to create')

    args = parser.parse_args()

    # paths
    dest = os.path.join(Config.DATA, args.feature)

    print("Cleaning destination directory {}".format(dest))

    # clean destination directory
    if os.path.exists(dest):
        shutil.rmtree(dest)
        os.makedirs(dest)
    else:
        os.makedirs(dest)

    # Load the exported data
    print("Importing data from {}".format(args.source))
    labels, all_features = loadRData(args.source)

    # Write one feature file per author
    for author in set(labels):
        dest_file = os.path.join(dest, author + '.json')
        print('Writing {}'.format(dest_file))
        with open(dest_file, 'w') as f:
            json.dump(list(all_features[labels==author]), f, indent=1)

    # get feature counts
    print("Generating feature counts")
    counts = Counter([feat for line in all_features for feat in line])

    # create gensim dictionary
    dict_file = os.path.join(dest, 'gensim.dict')
    print('Writing dictionary {}'.format(dict_file))

    dictionary = gensim.corpora.Dictionary(all_features)
    #dictionary.filter_extremes(keep_n=400)
    dictionary.save(dict_file)

    # write word counts
    count_file = os.path.join(dest, 'wordCounts.tsv')
    print('Writing feature counts to {}'.format(count_file))

    with open(count_file, 'w') as f:
        for word,count in counts.most_common():
            line = word + '\t' + str(count) + '\n'
            f.write(line)
