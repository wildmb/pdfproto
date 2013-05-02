#!/usr/bin/env python

# standard library imports
from contextlib import closing
import mmap
from tempfile import NamedTemporaryFile

# third party related imports
import pytest

# local library imports
from pdfproto.parser.pdf_objects import *
from pdfproto.parser.PDFLexer import PDFLexer

class TestPDFStreamObject:

    def test_decode(self):

        test_data = """\
7342 0 obj
<</DecodeParms<</Columns 5/Predictor 12>>/Filter/FlateDecode/ID[<5FC47DB1E9FC42E4990C818A453E009A><1C2BCADD5BB547BA849DAD158DE8DFD0>]/Index[375 1 1482 1 7112 1 7328 15]/Info 7112 0 R/Length 73/Prev 20448229/Root 7114 0 R/Size 7343/Type/XRef/W[1 4 0]>>stream
h\xdebbd\xb4`\xcdgb```\xaecb\xfc\x7fB\xe4\x00\xd3\x7fF\x8b_\xf3A"\xb2\x06 \x92\xa9\x1bD28\x82Ik0i\x02&\xf5A$\xa3%\x82\xcd\xa0\x07&\xcd\x11lF\x1d0\xdb\x08\xcc\xbe\x0f\x10`\x00\xfd\x99\n\xb5
endstream
endobj"""

        with closing(NamedTemporaryFile()) as f:
            f.write(test_data)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                obj = p.get_indirect_object(0)
                assert obj.object_num == 7342
                assert obj.generation_num == 0

                stream_obj = obj.data
                stream_dict = stream_obj.stream_dict.data

                assert stream_dict['DecodeParms'] == {'Columns': 5, 'Predictor': 12}
                assert stream_dict['Filter'] == 'FlateDecode'
                assert stream_dict['Index'] == [375, 1, 1482, 1, 7112, 1, 7328, 15]
                assert stream_dict['Info'] == (7112, 0)
                assert stream_dict['Length'] == 73
                assert stream_dict['Prev'] == 20448229
                assert stream_dict['Root'] == (7114, 0)
                assert stream_dict['Size'] == 7343
                assert stream_dict['Type'] == 'XRef'
                assert stream_dict['W'] == [1, 4, 0]

                stream_data = stream_obj.decode()

