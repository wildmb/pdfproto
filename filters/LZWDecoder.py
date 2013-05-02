#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from pdfproto.filters.Predictor import Predictor
from pdfproto.utils import BitReader, BitReaderError


class LZWDecoder:
    """Decode data that has been encoded using LZW compression method.

    Rewrite from pdfminer

    Attributes:

    """

    def __init__(self, **decode_args):

        self.nbits = 9
        self.table = None
        self.prev_buffer = None
        self.decode_params = decode_args

    def decode(self, data):

        ret = []
        bit_reader = BitReader(data)

        while bit_reader.bit_pos < len(bit_reader):
            code = bit_reader.read(self.nbits)
            ret.append(self._feed(code))

        return self._post_predict(''.join(ret))

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

    def _post_predict(self, decoded):

        predictor = self.decode_params.get('Predictor', 1)
        colors = self.decode_params.get('Colors', 1)
        bits_per_component = self.decode_params.get('BitsPerComponent', 8)
        columns = self.decode_params.get('Columns', 1)
        early_change = self.decode_params.get('EarlyChange', 1)

        # TODO: support early_change

        return Predictor.post_predict(decoded, predictor, colors,
                                      bits_per_component, columns)