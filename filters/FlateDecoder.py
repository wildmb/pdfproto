#!/usr/bin/env python

# standard library imports
import zlib

# third party realted imports

# local library imports
from pdfproto.filters.Predictor import Predictor


class FlateDecoder:

    def __init__(self, **decode_args):

        self.decode_params = decode_args

    def decode(self, data):

        return self._post_predict(zlib.decompress(data))

    def _post_predict(self, decoded):

        predictor = self.decode_params.get('Predictor', 1)
        colors = self.decode_params.get('Colors', 1)
        bits_per_component = self.decode_params.get('BitsPerComponent', 8)
        columns = self.decode_params.get('Columns', 1)

        return Predictor.post_predict(decoded, predictor, colors,
                                      bits_per_component, columns)