#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import
from pdfproto.parser.PDFLexer import PDFLexerError
from pdfproto.trailer.PDFTrailer import PDFTrailer


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

        xref_dict = stream.data