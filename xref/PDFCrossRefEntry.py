#!/usr/bin/env python

# standard library imports
from collections import namedtuple
# third party related imports

# local library imports


PDFCrossRefEntry = namedtuple(
                        '_PDFCrossRefEntry',
                        ('offset', 'object_num', 'generation_num', 'state')
                   )

PDFCrossRefCompressedEntry = namedtuple(
                                '_PDFCrossRefCompressedEntry',
                                ('obj_stream_num', 'obj_index', 'object_num')
                             )
