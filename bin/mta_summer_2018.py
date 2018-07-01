'''Common project config and utilities
'''

import re
import os
import json

#
# Set default paths, CTS server here
#

class Config(object):
    '''Configuration values'''

    SERVER = 'http://cts.perseids.org/api/cts/'
    INDEX = os.path.join('conf', 'corpus.json')
    DATA = os.path.join('data', 'corpus')


class Text(object):
    '''Metadata for one text'''

    def __init__(self, author=None, title=None, lang=None, urn=None):
        self.author = author
        self.title = title
        self.lang = lang
        self.urn = urn
        self.lines = None
        self.loci = None


    def __repr__(self):
        return('<Text {}: {} {}>'.format(self.urn, self.author, self.title))


    def dataFromJson(self, file):
        '''Load loci and verse lines from JSON file'''

        # wipe any existing data
        self.loci = []
        self.lines = []

        # read from the JSON files
        with open(file) as f:
            data = json.load(f)
            for loc, verse in data:
                self.loci.append(loc)
                self.lines.append(verse)


    @classmethod
    def metaFromDict(self, rec):
        '''Create a new text object from a dictionary'''

        return self(
            author = rec.get('author', None),
            title = rec.get('title', None),
            lang = rec.get('lang', None),
            urn = rec.get('cts_urn', None)
        )
