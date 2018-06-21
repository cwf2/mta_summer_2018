#!/usr/bin/env python3
''' Retrieve the corpus from remote CTS server
'''

#
# import statements
#

import os
import json

from MyCapytain.resolvers.cts.api import HttpCtsResolver
from MyCapytain.retrievers.cts5 import HttpCtsRetriever

from mta_summer_2018 import Config, Text

#
# global values
#


#
# functions
#

def download_and_save(resolver, urn, path):
    '''Download a remote text and save locally'''

    print('Downloading {}...'.format(urn))

    # Get references to books
    #  (all our texts are of `book.line` format)
    books = resolver.getReffs(urn)

    # Flatten the whole poem into a list of lines
    all_lines = []
    
    for i, book in enumerate(books):
        cts_passage = resolver.getTextualNode(urn, subreference=book)
        
        print(" - book {}/{}".format(i+1, len(books)))
        
        xml = cts_passage.export('python/lxml')
        
        for l in xml.iter('{http://www.tei-c.org/ns/1.0}l'):
            all_lines.append((
                '{}.{}'.format(book, l.get('n')),
                l.xpath('string()').strip()
            ))

    print('Saving to {}'.format(path))
        
    with open(path, 'w') as f:
        json.dump(all_lines, f, indent=4)
    

#
# main
#

if __name__ == '__main__':
    
    # Read the corpus metadata
    with open(Config.INDEX) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    
    # Create a Resolver instance
    resolver = HttpCtsResolver(HttpCtsRetriever(Config.SERVER))
    
    for work in corpus:
        print('📜 {} {}'.format(work.author, work.title))
        download_and_save(
            resolver = resolver,
            urn = work.urn, 
            path = os.path.join(Config.DATA, 'corpus', work.author + '.json')
        )
        print()
