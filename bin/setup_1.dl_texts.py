#!/usr/bin/env python3
'''Setup models and corpus

   Download the Latin models required for CLTK.
'''

#
# import statements
#

import os
import shutil
import json
import argparse
import sys
from lxml import etree

from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text

#
# functions
#

def retrieveXML(resolver, text, dest):
    '''Download a remote work and save individual books as local xml'''

    print('Downloading {} {}'.format(text.author, text.title))
    
    if not os.path.exists(dest):
        os.mkdir(dest)
    
    # Get references to books
    #  (all our texts are of `book.line` format)
    books = resolver.getReffs(text.urn)

    # download one book at a time
    for i, book in enumerate(books):

        print(" - fetching book {}/{}".format(i+1, len(books)))
        ctsPassage = resolver.getTextualNode(text.urn, subreference=book)

        # extract xml and save
        xml = ctsPassage.export('python/lxml')
        
        filename = os.path.join(dest, '{i:02d}_{urn}-{book}.xml'.format(
            i=i, urn=text.author, book=book))
        
        print(' - saving to {}'.format(filename))
        with open(filename, 'wb') as f:
            f.write(etree.tostring(xml, encoding = 'utf-8', pretty_print = True))
    
#
# Main
#

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Install corpus and CLTK models'
    )
    parser.add_argument('--server', 
        metavar='URL', type=str, default=Config.SERVER,
        help='remote CTS server')
    parser.add_argument('--index', 
        metavar="FILE", default=Config.INDEX,
        help='corpus index file')
    parser.add_argument('--corpus', 
        metavar="DIR", default=Config.DATA,
        help='local corpus directory')

    args = parser.parse_args()

    # clean destination directory
    dest = os.path.join(args.corpus, 'xml')
    if os.path.exists(dest):
        shutil.rmtree(dest)
        os.makedirs(dest)
    else:
        os.makedirs(dest)

    # Read the corpus metadata
    with open(args.index) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    
    # Create a Resolver instance
    resolver = HttpCtsResolver(HttpCtsRetriever(args.server))
    
    for text in corpus:
        retrieveXML(resolver, text, os.path.join(dest, text.author))
        print()
    