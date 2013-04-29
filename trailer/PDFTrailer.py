#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import


class PDFTrailer:
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

    def __init__(self):
        self.size = 0
        self.prev = None
        self.root = None
        self.encrypt = False
        self.info = None
        self.id = None
        self.offset = None

    def load_trailer_dict(self, trailer_dict):

        # shall not be an indirect reference
        if 'Size' in trailer_dict:
            self.size = trailer_dict['Size']

        # present only if the file has more than 1 cross reference
        # section
        if 'Prev' in trailer_dict:
            self.prev = trailer_dict['Prev']

        # shall be an indirect reference
        if 'Root' in trailer_dict:
            self.root = trailer_dict['Root']

        # required if document is encrypted
        if 'Encrypt' in trailer_dict:
            self.encrypt = trailer_dict['Encrypt']

        # shall be an indirect reference
        if 'Info' in trailer_dict:
            self.info = trailer_dict['Info']

        # required if an Encrypt entry is presented
        if 'ID' in trailer_dict:
            self.id = trailer_dict['ID']