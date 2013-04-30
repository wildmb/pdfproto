#!/usr/bin/env python

# standard library imports

# third party related imports
import pytest

# local library imports
from pdfproto.filters.RunLengthDecoder import RunLengthDecoder

class TestRunLengthDecoder:

    def test_decode(self):

        test_data = (
            ('\x05123456\xfa7\x04abcde\x80junk', '1234567777777abcde'),
        )

        r = RunLengthDecoder()
        for encoded, decoded in test_data:
            assert r.decode(encoded) == decoded
