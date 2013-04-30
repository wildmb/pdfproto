#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


class LZWDecoder:
    """Decode data that has been encoded using LZW compression method.

    Rewrite from pdfminer

    Attributes:
        buffer: A byte read from the encoded data.
        bit_pos: The number of read bits in above buffer.
        byte_pos: The index of encoded data.

    """

    def __init__(self):

        self.buffer = 0
        self.bit_pos = 8
        self.byte_pos = 0
        self.nbits = 9
        self.table = None
        self.prev_buffer = None

    def decode(self, data):

        ret = []

        while self.byte_pos < len(data):
            code = self._read_bits(data, self.nbits)
            ret.append(self._feed(code))

        return ''.join(ret)

    def _read_bits(self, data, num_bits):

        value = 0

        while True:
            # number of remaining bits we can get from the
            # current buffer
            r = 8 - self.bit_pos

            if num_bits <= r:
                # read from buffer
                value = (value << num_bits) | \
                        (self.buffer >> (r - num_bits) & ((1 << num_bits) - 1))
                self.bit_pos += num_bits
                break
            else:
                # run out of buffer, read from encoded data
                value = (value << r) | (self.buffer & ((1 << r) - 1))
                num_bits -= r
                self.buffer = ord(data[self.byte_pos])
                self.byte_pos += 1
                self.bit_pos = 0

        return value

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
