#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import
from pdfproto.parser.PDFLexer import PDFLexerError
from pdfproto.trailer.PDFCrossRefTrailer import PDFCrossRefTrailer


class PDFCrossRefStreamError(Exception): pass


class PDFCrossRefStream:
    """

    Attributes:
        offset_dict: A dict maps (object_num, generation_num) -> int
        free_dict: A dict maps (object_num, generation_num) -> bool
        trailer: An instance of PDFTrailer

    """

    def __init__(self):

        self.offset_dict = {}

        # TODO: maybe we don't need this
        self.free_dict = {}

        self.trailer = None

    def load_stream(self, parser, xref_pos):
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
                    self.offset_dict[(obj_num, field_2)] = field_1
                    self.free_dict[(obj_num, field_2)] = True
                elif entry_type == 1:
                    self.offset_dict[(obj_num, field_2)] = field_1
                    self.free_dict(obj_num, field_2)] = False
                elif entry_type == 2:
                    self.offset_dict[(obj_num, field_2)] = (field_1, field2)
                    self.free_dict[(obj_num, field_2)] = False
                else:
                    raise PDFCrossRefStreamError(('invalid cross reference'
                                                  'stream entry type: %s'),
                                                 entry_type)

                obj_num += 1
                num_remaining -= 1

    def _to_int(self, str_data):
        """Convert multiple bytes to integer.

        >>> self._to_int('abc')
        >>> 6382179

        """

        ret = 0
        for s in str_data:
            ret = ret * 8 + ord(s)

        return ret