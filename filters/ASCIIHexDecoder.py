#!/usr/bin/env python

# standard library imports
import binascii
import re

# third party related imports

# local library imports


class ASCIIHexDecoder:
    """PDF ASCIIHexDecode Filter."""

    # Only hexadecimal character and EOD('>') is allowed
    RE_IGNORE = re.compile(r'[^\da-fA-F>]')

    def decode(self, data):
        """Decode ASCII hexaecimal form data.

        Decodes data that has been encoded in ASCII hexadecimal form.
        All white-space characters shall be ignored.

        Args:
            data: A sequence of bytes.

        Returns:
            A sequence of byte.

        """

        # sanitize data
        clean_data = self.RE_IGNORE.sub('', data)
        eod_ix = clean_data.rfind('>')
        if eod_ix != -1:
            clean_data = clean_data[:eod_ix]

        # ensure even length
        if len(clean_data) % 2 == 1:
            clean_data += '0'

        return binascii.unhexlify(clean_data)

