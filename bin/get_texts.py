#!/usr/bin/env python3
''' Retrieve the corpus from remote CTS server
'''

#
# import statements
#

import os
import json
import argparse
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

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
        
        #save this
        xml = cts_passage.export('python/lxml')
        
        ###
        
        for l in xml.iter('{http://www.tei-c.org/ns/1.0}l'):
            all_lines.append((
                '{}.{}'.format(book, l.get('n')),
                l.xpath('string()').strip()
            ))

    print('Saving to {}'.format(path))
        
    with open(path, 'w') as f:
        json.dump(all_lines, f, indent=4)
        
        
#gets files from internet, download urn from resolver       
def retrieve(resolver, urn, filename):
    
    books = resolver.getReffs(urn)
    #filename = 'xml Files'
    
    #vergil_1.xml
    
    for i, book in enumerate(books):
        ctsPassage = resolver.getTextualNode(urn, subreference=book)
        xml = ctsPassage.export('python/lxml')
    
        with open('{}_{:02d}.xml'.format(filename, int(book)), 'wb') as f:
            f.write(etree.tostring(xml, encoding = 'utf-8', pretty_print = True))
            #print(type(etree.tostring(xml)))
            #print(etree.tostring(xml))
            
    
    
    
    
#takes xml file as an argument    
def write(xmlFile, jsonFile):
    
    xml = etree.parse(xmlFile).getroot()
    all_lines = []
    book = 0
    
    for l in xml.iter('{http://www.tei-c.org/ns/1.0}l'):
        for note in l.iter('{http://www.tei-c.org/ns/1.0}note'):
            tail = note.tail
            note.clear()
            note.tail = tail
        all_lines.append(('{}.{}'.format(book, l.get('n')), l.xpath('string()').strip()))

    print('Saving to {}'.format(json_file))
        
    with open(jsonFile, 'w') as f:
        json.dump(all_lines, f, indent=4) 
            
    

#
# main
#

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Populate corpus from remote CTS server'
    )
    parser.add_argument('--server', 
        metavar='URL', type=str, default=Config.SERVER_URL,
        help='remote CTS server')
    parser.add_argument('--index', 
        metavar="FILE", default=Config.INDEX_PATH,
        help='corpus index file')
    parser.add_argument('--dest', 
        metavar="DIR", default=Config.LOCAL_BASE,
        help='local corpus directory')

    args = parser.parse_args()

    # Read the corpus metadata
    with open(args.index) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    
    # Create a Resolver instance
    resolver = HttpCtsResolver(HttpCtsRetriever(args.server))
    
#    for work in corpus:
#        print('📜 {} {}'.format(work.author, work.title))
#        retrieve(
#            resolver = resolver,
#            urn = work.urn, 
#            filename = os.path.join(args.dest, work.author)
#        )
#        print()
    xml_files = [f for f in os.listdir(args.dest) if f.endswith('.xml')]
    for fileName in xml_files:
        xml_file = os.path.join(args.dest, fileName)
        json_file = os.path.join(args.dest, fileName.replace('.xml', '.json'))
        write(xml_file, json_file)
        