#!/usr/bin/env python

# standard library imports

# third party related imports
import pytest

# local library imports
from pdfproto.filters.LZWDecoder import LZWDecoder


class TestLZWDecoder:

    def test_decode(self):

        test_data = (
            ('\x80\x0b\x60\x50\x22\x0c\x0c\x85\x01',
             '\x2d\x2d\x2d\x2d\x2d\x41\x2d\x2d\x2d\x42'),
        )

        lzw = LZWDecoder()

        for encoded, decoded in test_data:
            assert lzw.decode(encoded) == decoded
