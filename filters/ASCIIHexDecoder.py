#!/usr/bin/env python

# standard library imports
import re

# third party related imports

# local library imports


class ASCIIHexDecoder:

    RE_HEX = re.compile(r'([a-f\d]{2})', re.IGNORECASE)

    RE_TRAIL = re.compile(r'^(?:[a-f\d]{2}|\s)*([a-f\d])[\s>]*$', re.IGNORECASE)

    def decode(self, data):

        out = map(lambda hx: chr(int(hx, 16)), self.RE_HEX.findall(data))
        match_obj = self.RE_TRAIL.search(data)

