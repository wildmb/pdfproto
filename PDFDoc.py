#!/usr/bin/env python

# standard library import

# third party related import

# local library import
from parser import PDFParser


class PDFDoc:
    """PDFDoc

    PDFDoc contains pdf catelog, pages.

    Attributes:
        parser: An instance of PDFParser.

    """

    def __init__(self):

        self.name = None
        self.parser = None
        self.pages = []

    def open(self, name):
        """Open a pdf file."""

        self.name = name
        self.parser = PDFParser()
        self.parser.open(name)