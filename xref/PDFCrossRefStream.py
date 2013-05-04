#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import
from pdfproto.parser.PDFLexer import PDFLexerError
from pdfproto.trailer.PDFCrossRefTrailer import PDFCrossRefTrailer
from pdfproto.xref.PDFCrossRefEntry import (PDFCrossRefEntry,
                                            PDFCrossRefCompressedEntry)


class PDFCrossRefStreamError(Exception): pass


class PDFCrossRefStream:
    """

    Attributes:
        entries: A list of instances of PDFCrossRefEntry or
            PDFCrossRefCompressedEntry.
        trailer: An instance of PDFTrailer

    """

    def __init__(self):

        self.entries = []
        self.trailer = None

    def parse(self, parser, xref_pos):
        """Load cross reference stream

        Args:
            parser: An instance of PDFParser
            xref_pos: An integer that cross reference table starts.

        """

        try:
            stream = parser.lexer.get_indirect_object(xref_pos)
        except PDFLexerError, e:
            logger.error('Should be an indirect object')
                raise PDFCrossRefSectionError('Should be an indirect object')

        stream = stream.data

        self.trailer = PDFCrossRefTrailer(stream.stream_dict)

        # get decoded data
        xref_data = stream.get_decoded_data()
        xref_data_ptr = 0

        xref_size = self.trailer.size
        xref_index = self.trailer.index
        xref_prev = self.trailer.prev
        xref_w = self.trailer.w
        sum_w_bytes = sum(xref_w)

        for i in xrange(0, len(xref_index), 2):
            obj_num, num_remaining = xref_index[2 * i], xref_index[2 * i + 1]

            while num_remaining > 0:
                entry = xref_data[xref_data_ptr:(xref_data_ptr + sum_w_bytes)]
                xref_data_ptr += sum_w_bytes

                if xref_w[0] == 0:
                    entry_type = 1
                else:
                    entry_type = self._to_int(entry[:xref_w[0]])

                field_1 = self._to_int(entry[xref_w[0]:xref_w[1]])
                field_2 = self._to_int(entry[xref_w[1]:])

                if entry_type == 0:
                    entry = PDFCrossRefEntry(field_1, obj_num,
                                             field_2, 'f')
                elif entry_type == 1:
                    entry = PDFCrossRefEntry(field_1, obj_num,
                                             field_2, 'n')
                elif entry_type == 2:
                    entry = PDFCrossRefCompressedEntry(field_1, field_2)
                else:
                    raise PDFCrossRefStreamError(('invalid cross reference'
                                                  'stream entry type: %s'),
                                                 entry_type)

                self.entries.append(entry)
                obj_num += 1
                num_remaining -= 1

    def _to_int(self, str_data):
        """Convert multiple bytes to integer.

        >>> self._to_int('abc')
        >>> 6382179

        """

        ret = 0
        for s in str_data:
            ret = ret * 256 + ord(s)

        return ret
