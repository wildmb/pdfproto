#!/usr/bin/env python

# standard library imports
import binascii

# third party related imports
import pytest

# local library imports
from pdfproto.filters.ASCIIHexDecoder import ASCIIHexDecoder


class TestASCIIHexDeocder:

    def test_decode(self):

        test_data = {
                '5768617420746865206675636b21': 'What the fuck!',
                '57\r68\n61\t74\b20\v74 68  65  206675636b21': 'What the fuck!',
                '5768617420746865206675636b21>': 'What the fuck!',
                '5768617420746865206675636b21 >': 'What the fuck!',
                '>': '',
                '': '',
        }

        decoder = ASCIIHexDecoder()

        for key in test_data:
            assert decoder.decode(key) == test_data[key]
