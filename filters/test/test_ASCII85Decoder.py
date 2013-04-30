#!/usr/bin/env python

# standard library imports

# third party related imports
import pytest

# local library imports
from pdfproto.filters.ASCII85Decoder import ASCII85Decoder


class TestASCII85Deocder:

    def test_decode(self):

        test_data = {
                '9jqo^BlbD-BleB1DJ+*+F(f,q': 'Man is distinguished',
                'E,9)oF*2M7/c~>': 'pleasure.',
        }

        decoder = ASCII85Decoder()

        for key in test_data:
            assert decoder.decode(key) == test_data[key]

