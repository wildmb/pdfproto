#!/usr/bin/env python

# standard library imports
from contextlib import closing
import mmap
import random
from tempfile import NamedTemporaryFile

# third party related imports

# local library imports
from pdfproto.parser.PDFParser import PDFParser
from pdfproto.trailer.PDFTrailer import PDFTrailer
from pdfproto.xref.PDFCrossRefSection import (PDFCrossRefEntry,
                                              PDFCrossRefSection)


class TestPDFCrossRefStream:

    def test_parse_1(self):
        pass

