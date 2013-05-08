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
from pdfproto.xref.PDFCrossRefEntry import (PDFCrossRefEntry,
                                            PDFCrossRefCompressedEntry)
from pdfproto.xref.PDFCrossRefStream import PDFCrossRefStream


class TestPDFCrossRefStream:

    def test_parse_1(self):

        test_data = """\
1 0 obj
<<
    /Type /XRef
    /Size 100
    /Index [2 10]
    /W [1 2 1]
    /Filter /ASCIIHexDecode
>>
stream
01 0E8A 00
02 0002 00
02 0002 01
02 0002 02
02 0002 03
02 0002 04
02 0002 05
02 0002 06
02 0002 07
01 1323 0
endstream
endobj
"""

        entries = (
                PDFCrossRefEntry(3722, 2, 0, 'n'),
                PDFCrossRefCompressedEntry(3, 2, 0),
                PDFCrossRefCompressedEntry(4, 2, 1),
                PDFCrossRefCompressedEntry(5, 2, 2),
                PDFCrossRefCompressedEntry(6, 2, 3),
                PDFCrossRefCompressedEntry(7, 2, 4),
                PDFCrossRefCompressedEntry(8, 2, 5),
                PDFCrossRefCompressedEntry(9, 2, 6),
                PDFCrossRefCompressedEntry(10, 2, 7),
                PDFCrossRefEntry(4899, 11, 0, 'n'),
        )

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                parser = PDFParser()
                parser.open(f.name)

                xref = PDFCrossRefStream()
                xref.parse(parser, 0)

                assert xref.trailer.size == 100
                assert xref.trailer.prev is None
                assert xref.trailer.root is None
                assert xref.trailer.encrypt is None
                assert xref.trailer.info is None
                assert xref.trailer.id is None
                assert xref.trailer.index == [2, 10]
                assert xref.trailer.w == [1, 2, 1]
                assert xref.trailer.xref_stream is None

                for ix, entry in enumerate(xref.entries):
                    assert entry == entries[ix]
