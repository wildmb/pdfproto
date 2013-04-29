#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import
from pdfproto.trailer.PDFTrailer import PDFTrailer


class PDFCrossRefTrailer(PDFTrailer):
    """The PDF trailer.

    Attributes:
        size: The number one greater than the highest object number used
            in this section or in any section for which this shall be an
            update. It shall be equivalent to the Size entry in a
            trailer dictionary.
        index: An array containing a pair of integers for each
            subsection in this section. The first integer shall be the
            first object number in the subsection; the second integer
            shall be the number of entries in the subsection. Default
            value: [0 size].
        prev: The byte offset in the decoded stream from the beginning
            of the file to the beginning of the previous cross reference
            stream. This entry has the same function as the Prev entry
            in the trailer dictionary.
        W: An array of integers representing the size of the fields in a
            single cross reference entry. A value of zero for an element
            in the W array indicates that the corresponding field shall
            not be present in the stream, and the default value shall be
            used, if there is one. If the first element is zero, the
            type field shall not be present, and shall default to type 1.
        xref_stream: The byte offset in the decoded stream from the
            beginning of the file of a cross reference stream.

    """

    def __init__(self, trailer_dict):

        super(PDFCrossRefTrailer, self).__init__(trailer_dict)

    @property
    def index(self):
        """[first object number, number of entries]."""

        return self.trailer_dict.get('Index')

    @property
    def w(self):
        """[number of byte of each entry]"""

        return self.trailer_dict.get('W')