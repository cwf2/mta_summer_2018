'''Common project config and utilities
'''

import os
import json

#
# Set default paths, CTS server here
#

class Config(object):
    '''Configuration values'''
    
    SERVER_URL = 'http://cts.perseids.org/api/cts/'
    INDEX_PATH = os.path.join('conf', 'corpus.json')
    LOCAL_BASE = os.path.join('data', 'corpus')


class Text(object):
    '''Metadata for one text'''
    
    def __init__(self, author=None, title=None, lang=None, urn=None):
        self.author = author
        self.title = title
        self.lang = lang
        self.urn = urn
    
    
    def __repr__(self):
        return('<Text {}: {} {}>'.format(self.urn, self.author, self.title))
    
    @classmethod
    def fromDict(self, rec):
        '''Create a new text object from a dictionary'''
        
        return self(
            author = rec.get('author', None),
            title = rec.get('title', None),
            lang = rec.get('lang', None),
            urn = rec.get('cts_urn', None)
        )
