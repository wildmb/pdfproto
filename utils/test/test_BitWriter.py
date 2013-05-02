#!/usr/bin/env python

# standard library imports
import random

# third party realted imports
import pytest

# local library imports
from pdfproto.utils.BitWriter import BitWriter, BitWriterError


class TestBitWriter:

    def _rand_data(self, data_len):

        return map(lambda _: random.randint(0, 255), xrange(data_len))

    def test_write(self):

        # test empty data
        bw = BitWriter()
        bw.flush()
        assert str(bw) == ''

        # write random data
        data = self._rand_data(random.randint(0, 255))
        bitmap = []
        for d in data:
            bits = '0' * random.randint(0, 10) + bin(d)[2:]
            bitmap.append(bits)
            bw.write(d, len(bits))

        bw.flush()

        # generate bitmap
        bitmap = ''.join(bitmap)
        if len(bitmap) % 8 != 0:
            bitmap += '0' * (8 - (len(bitmap) % 8))

        # generate expect answer
        expect_chars = []
        for i in xrange(0, len(bitmap), 8):
            expect_chars.append(chr(int(bitmap[i:(i + 8)], 2)))

        assert str(bw) == ''.join(expect_chars)

    def test_len(self):

        bw = BitWriter()
        assert len(bw) == 0

        data = self._rand_data(random.randint(0, 255))
        bitmap = []
        for d in data:
            bits = '0' * random.randint(0, 10) + bin(d)[2:]
            bitmap.append(bits)
            bw.write(d, len(bits))

        assert len(bw) == len(''.join(bitmap))
