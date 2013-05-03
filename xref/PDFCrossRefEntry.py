#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


class PDFCrossRefEntry(object):
    """PDF cross reference entry

    Attributes:
        object_num:

    """

    FREE = 'f'
    IN_USE = 'n'

    def __init__(self, obj_num, gen_num, state):

        self.object_num = obj_num
        self.generation_num = gen_num
        self.state = state

        if state != self.FREE and state != self.IN_USE:
            raise ValueError('state should be either "f" or "n"')
