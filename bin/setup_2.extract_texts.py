#!/usr/bin/env python3
''' Retrieve the corpus from remote CTS server
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

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from mta_summer_2018 import Config, Text


#
# functions
#
    
#takes xml file as an argument    
def parseXML(xmlFile):
    '''Parse a local xml file'''
    
    xml = etree.parse(xmlFile).getroot()
    lines = []
    book_n = 0
    
    for l in xml.iter('{http://www.tei-c.org/ns/1.0}l'):
        for note in l.iter('{http://www.tei-c.org/ns/1.0}note'):
            tail = note.tail
            note.clear()
            note.tail = tail
        line_n = l.get('n')
        lines.append(('{}.{}'.format(book_n, line_n), l.xpath('string()').strip()))

    return lines
    
#
# main
#

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Populate corpus from remote CTS server'
    )
    parser.add_argument('--index', 
        metavar="FILE", default=Config.INDEX,
        help='corpus index file')
    parser.add_argument('--corpus', 
        metavar="DIR", default=Config.DATA,
        help='local corpus directory')

    args = parser.parse_args()

    # clean destination directory
    dest = os.path.join(args.corpus, 'lines')
    if os.path.exists(dest):
        shutil.rmtree(dest)
        os.makedirs(dest)
    else:
        os.makedirs(dest)

    # Read the corpus metadata
    with open(args.index) as f:
        corpus = [Text.metaFromDict(rec) for rec in json.load(f)]
    
    # process the texts
    for text in corpus:
        print('Processing {} {}'.format(text.author, text.title))

        source = os.path.join(args.corpus, 'xml', text.author)

        xml_files = [f for f in os.listdir(source) if f.endswith('.xml')]
        all_lines = []

        for i, file in enumerate(sorted(xml_files)):
            print(' - reading part {}/{}'.format(i, len(xml_files)))
            lines = parseXML(os.path.join(source, file))
            all_lines.extend(lines)

        # save verse lines
        line_file = os.path.join(dest, text.author + '.json')
        print(' - saving {}'.format(line_file))
        with open(line_file, 'w') as f:
            json.dump(all_lines, f, indent=1)
        
