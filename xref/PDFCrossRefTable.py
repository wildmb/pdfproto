#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import
from PDFCrossRenEntry import PDFCrossRefEntry, PDFCrossRefCompressedEntry


class PDFCrossRefTableError(Exception): pass


class PDFCrossRefTable:

    def __init__(self, lexer):

        self.lexer = lexer
        self.objects = {}
        self.trailers = []

    def _add_object(self, obj_num, gen_num, offset):

        obj_key = (entry.object_num, entry.generation_num)

        if obj_key in self.objects:
            logger.warn('(%s, %s) already exists', *obj_key)
            return

        self.objects[obj_key] = offset

    def merge_xrefs(self, xrefs):

        for xref in xrefs:
            self.trailers.append(xref.trailer)

            for entry in xref.entries:
                if isinstance(entry, PDFCrossRefEntry):
                    if entry.object_num == 0:
                        continue

                    if entry.state == 'n':
                        self._add_object(entry.object_num,
                                         entry.generation_num,
                                         entry)

                    elif entry.state == 'f':
                        for g in xrange(entry.generation_num + 1):
                            self._add_object(entry.object_num,
                                             entry.generation_num,
                                             None)
                    else:
                        logger.error('unknown entry.state = %s', entry.state)

                elif isinstance(entry, PDFCrossRefCompressedEntry):
                    self._add_object(entry.object_num, 0, entry)

                else:
                    logger.error('not a valid xref entry %s', entry)

