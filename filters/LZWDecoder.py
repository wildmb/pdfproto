#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from pdfproto.utils import BitReader, BitReaderError


class LZWDecoder:
    """Decode data that has been encoded using LZW compression method.

    Rewrite from pdfminer

    Attributes:

    """

    def __init__(self):

        self.nbits = 9
        self.table = None
        self.prev_buffer = None

    def decode(self, data):

        ret = []
        bit_reader = BitReader(data)

        while bit_reader.bit_pos < len(bit_reader):
            code = bit_reader.read(self.nbits)
            ret.append(self._feed(code))

        return ''.join(ret)

    def _feed(self, code):

        ret = ''

        if code == 256:
            self.table = [chr(i) for i in xrange(256)]
            self.table.append(None)
            self.table.append(None)
            self.prev_buffer = ''
            self.nbits = 9
        elif code == 257:
            pass
        elif not self.prev_buffer:
            ret = self.prev_buffer = self.table[code]
        else:
            if code < len(self.table):
                ret = self.table[code]
                self.table.append(self.prev_buffer + ret[0])
            else:
                self.table.append(self.prev_buffer + self.prev_buffer[0])
                ret = self.table[code]

            table_len = len(self.table)
            if table_len == 511:
                self.nbits = 10
            elif table_len == 1023:
                self.nbits = 11
            elif table_len == 2047:
                self.nbits = 12

            self.prev_buffer = ret

        return ret
