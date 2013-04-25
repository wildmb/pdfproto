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

    """

    def __init__(self):
        self.size = 0
        self.prev = None
        self.root = None
        self.encrypt = False
        self.info = None
        self.id = None