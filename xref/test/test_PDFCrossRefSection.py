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


class TestPDFCrossRefSection:

    def test_parse_1(self):

        test_data = """\
xref
0 6
0000000003 65535 f
0000000017 00000 n
0000000081 00000 n
0000000000 00007 f
0000000331 00000 n
0000000409 00000 n
% I AM COMMENT
trailer
<<>>"""

        entries = (
                PDFCrossRefEntry(3, 0, 65535, 'f'),
                PDFCrossRefEntry(17, 1, 0, 'n'),
                PDFCrossRefEntry(81, 2, 0, 'n'),
                PDFCrossRefEntry(0, 3, 7, 'f'),
                PDFCrossRefEntry(331, 4, 0, 'n'),
                PDFCrossRefEntry(409, 5, 0, 'n'),
        )

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                parser = PDFParser()
                parser.open(f.name)

                xref = PDFCrossRefSection()
                xref.parse(parser, 0)
                print xref.trailer.__dict__

                for ix, entry in enumerate(entries):
                    assert entry == xref.entries[ix]

                assert xref.trailer.trailer_dict == {}

    def test_parse_2(self):

        test_data = """\
xref
0 1
0000000000 65535 f
3 1
0000025325 00000 n
23 2
0000025518 00002 n
0000025635 00000 n
30 1
0000025777 00000 n
% I AM REDUNDANCY
trailer
<<>>"""

        entries = (
                PDFCrossRefEntry(0, 0, 65535, 'f'),
                PDFCrossRefEntry(25325, 3, 0, 'n'),
                PDFCrossRefEntry(25518, 23, 2, 'n'),
                PDFCrossRefEntry(25635, 24, 0, 'n'),
                PDFCrossRefEntry(25777, 30, 0, 'n'),
        )

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                parser = PDFParser()
                parser.open(f.name)

                xref = PDFCrossRefSection()
                xref.parse(parser, 0)

                for ix, entry in enumerate(entries):
                    assert entry == xref.entries[ix]

                assert xref.trailer.trailer_dict == {}

    def test_parse_3(self):

        test_data = """\
xref
0 1
0000000000 65535 f
3 1
0000025325 00000 n
23 2
0000025518 00002 n
0000025635 00000 n
30 1
0000025777 00000 n
% I AM REDUNDANCY
trailer
<<
    /Size 22
    /Root 2 0 R
    /Info 1 0 R
    /ID [
            <746573742031>
            <746573742032>
        ]
>>"""

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                parser = PDFParser()
                parser.open(f.name)

                xref = PDFCrossRefSection()
                xref.parse(parser, 0)

                trailer = xref.trailer

        assert trailer.size == 22
        assert trailer.root == (2, 0)
        assert trailer.info == (1, 0)
        assert trailer.id == ['test 1', 'test 2']
