#!/usr/bin/env python

# standard library imports
import random

# third party related imports
import pytest

# local library imports
from pdfproto.utils.BitReader import BitReader, BitReaderError


class TestBitReader:

    def _rand_data(self, data_len):

        return map(lambda _: chr(random.randint(0, 255)), xrange(data_len))

    def _make_bitmap(self, data):

        ret = []

        for d in data:
            b = bin(ord(d))[2:]
            zero_size = 8 - len(b)
            ret.append('0' * zero_size + b)

        return ret

    def test_len(self):

        br = BitReader('')
        assert len(br) == 0

        # generate random data
        data_length = random.randint(0, 100)
        data = self._rand_data(data_length)

        br = BitReader(data)
        assert len(br) == 8 * data_length

    def test_peek(self):

        data_size = random.randint(0, 100)
        data = self._rand_data(data_size)
        data_bitmap = ''.join(self._make_bitmap(data))

        br = BitReader(data)

        with pytest.raises(BitReaderError):
            br.peek(-1)

        with pytest.raises(BitReaderError):
            br.peek(data_size * 8 + 1)

        for i in xrange(1, len(br)):
            assert br.peek(i) == int(data_bitmap[:i], 2)

    def test_read(self):

        data_size = random.randint(0, 100)
        data = self._rand_data(data_size)
        data_bitmap = self._make_bitmap(data)

        for d, b in zip(data, data_bitmap):
            assert ord(d) == int(b, 2)

        data_bitmap = ''.join(data_bitmap)

        br = BitReader(data)

        bits = len(br)
        while bits > 0:
            read_chunk = random.randint(0, bits)

            before_bit_pos = br.bit_pos
            read_out = br.read(read_chunk)
            after_bit_pos = br.bit_pos

            assert before_bit_pos + read_chunk == after_bit_pos
            if read_chunk == 0:
                assert read_out == 0
            else:
                assert read_out == \
                       int(data_bitmap[before_bit_pos:after_bit_pos], 2)

            bits -= read_chunk

