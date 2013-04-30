#!/usr/bin/env python

# standard library imports
import struct

# third party related imports

# local library imports


class ASCII85Decoder:
    """PDF ASCII85Decode Filter."""

    def decode(self, data):
        """Decode ASCII base-85 form data.

        Decodes data that has been encoded in ASCII base-85 form. All
        white-space characters shall be ignored. Rewrite from pdfminer.

        Args:
            data: A sequence of bytes.

        Returns:
            A sequence of byte.

        """

        n = b = 0
        out = ''
        for c in data:
            if '!' <= c <= 'u':
                n += 1
                b = b * 85 + ord(c) - 33
                if n == 5:
                    out += struct.pack('>L', b)
                    n = b = 0
            elif c == 'z':
                assert n == 0
                out += '\0\0\0\0'
            elif c == '~':
                if n:
                    for _ in xrange(5 - n):
                        b = b * 85 + 84
                    out += struct.pack('>L', b)[:(n - 1)]
                break

        return out
