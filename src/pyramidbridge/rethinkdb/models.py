"""Models for the RethinkDB"""
from collections import namedtuple

Binstore = namedtuple('Binstore',
                      'title, name, data, created, modified, appuserid')
