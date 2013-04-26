#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import


class PDFCrossRefTableError(Exception): pass


class PDFCrossRefTable:

    def __init__(self):

        self.offset_dict = {}
        self.free_dict = {}
