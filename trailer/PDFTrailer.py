#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import


class PDFTrailer(object):
    """The PDF trailer.

    Attributes:
        size: The total number of entries in the file's cross-reference
            table, as defined by the combination of the original
            section and all update sections.

        prev: The byte offset in the decoded stream from the beginning
            of the file to the beginning of the previous cross-reference
            section. If file has only one cross-reference section, it is
            None.

        root: The catalog dictionary for the PDF document.

        encrypt: The document's encryption dictionary.

        info: The document's information dictionary.

        id: An array of two byte-strings constituting a file identifier
            for the file. If there is no encrypt, it is None.

        offset: An integer representing the starting file position of
            the trailer.

    """

    def __init__(self, trailer_dict):

        self.trailer_dict = trailer_dict

    @property
    def size(self):
        """The total number of entries in the cross-reference table."""

        return self.trailer_dict.get('Size')

    @property
    def prev(self):
        """The byte offset of the previous cross-reference section."""

        return self.trailer_dict.get('Prev')

    @property
    def root(self):
        """The catalog dictionary."""

        return self.trailer_dict.get('Root')

    @property
    def encrypt(self):
        """The document's encryption dictionary."""

        return self.trailer_dict.get('Encrypt')

    @property
    def info(self):
        """The document's information dictionary."""

        return self.trailer_dict.get('Info')

    @property
    def id(self):
        """An array of file identifier for the file."""

        return self.trailer_dict.get('ID')