#!/usr/bin/env python

# standard library imports
from contextlib import closing
import mmap
import random
from tempfile import NamedTemporaryFile

# third party related imports

# local library imports
from ..PDFCrossRefSection import PDFCrossRefSection, PDFParser


class TestPDFCrossRefSection:

    def test_load_section1(self):

        test_data = """\
xref
0 6
0000000003 65535 f
0000000017 00000 n
0000000081 00000 n
0000000000 00007 f
0000000331 00000 n
0000000409 00000 n
I AM REDUNDANCY"""

        offset_dict = {
                (0, 65535): 3,
                (1, 0): 17,
                (2, 0): 81,
                (3, 7): 0,
                (4, 0): 331,
                (5, 0): 409
        }
        free_dict = {
                (0, 65535): False,
                (1, 0): True,
                (2, 0): True,
                (3, 7): False,
                (4, 0): True,
                (5, 0): True
        }

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                parser = PDFParser()
                parser.open(f.name)

                xref = PDFCrossRefSection()
                xref.load_section(parser, 0)

                assert xref.offset_dict == offset_dict
                assert xref.free_dict == free_dict

    def test_load_section(self):

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
I AM REDUNDANCY"""

        offset_dict = {
                (0, 65535): 0,
                (3, 0): 25325,
                (23, 2): 25518,
                (24, 0): 25635,
                (30, 0): 25777,
        }
        free_dict = {
                (0, 65535): False,
                (3, 0): True,
                (23, 2): True,
                (24, 0): True,
                (30, 0): True,
        }

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                parser = PDFParser()
                parser.open(f.name)

                xref = PDFCrossRefSection()
                xref.load_section(parser, 0)

                assert xref.offset_dict == offset_dict
                assert xref.free_dict == free_dict
