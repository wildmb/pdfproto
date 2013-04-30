#!/usr/bin/env python

# standard library imports
import zlib

# third party realted imports

# local library imports


class FlateDecoder:

    def decode(self, data):

        return zlib.decompress(data)
