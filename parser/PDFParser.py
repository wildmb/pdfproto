#!/usr/bin/env python

# standard library import
from contextlib import closing
import logging as logger
import mmap
import os

# third party related import

# local library import


class PDFParserError(Exception): pass


class PDFParser:
    """

    PDFParser parses the binary content of pdf document.

    Attribute:
        mmfile: A memory mapped file, ie. the document.

    """

    def __init__(self):

        self._file_obj = None
        self.mmfile = None

    def __del__(self):

        if self._file_obj is not None:
            self._file_obj.close()

        if self.mmfile is not None:
            self.mmfile.close()

    def open(self, name):
        """Open the specified pdf file.

        Args:
            name: A string denotes the pdf filename.

        """

        self._file_obj = open(name)
        self.mmfile = mmap.mmap(self._file_obj.fileno(), 0, prot=mmap.PROT_READ)

    def get_header(self):
        """Get the header of the pdf file.

        Returns:
            A string representing the file header. Must be "%PDF-1.[0-7]"

        """

        if self.mmfile.tell() != 0:
            self.mmfile.seek(0, os.SEEK_SET)

        header = self.mmfile.readline().rstrip()

        def is_valid_header(header):
            """Only %PDF-1.[0-7] is accepted."""

            return (len(header) == 8 and \
                    header.startswith('%PDF-1.') and \
                    header[7] in '01234567')

        # should test whether or not it is a valid pdf
        if not is_valid_header(header):
            raise PDFParserError('header is %s' % header)

        return header

    def _reverse_lines(self):
        """Yields lines in reverse order."""

        # go to the tail position
        self.mmfile.seek(0, os.SEEK_END)
        max_pos = self.mmfile.tell()
        end_pos = max_pos + 1

        while end_pos > 1:
            # find EOL
            carrage_ix = self.mmfile.rfind('\r', 0, end_pos)
            linefeed_ix = self.mmfile.rfind('\n', 0, end_pos)
            ix = max(carrage_ix, linefeed_ix)

            if ix == -1:
                yield self.mmfile[0:end_pos]
                break

            yield self.mmfile[min(ix + 1, max_pos):end_pos]

            curr_byte = self.mmfile[ix]
            if curr_byte == '\r':
                end_pos = ix
            else:
                if self.mmfile[max(0, ix - 1)] == '\r':
                    end_pos = ix - 1
                else:
                    end_pos = ix

    def _next_lines(self, start_pos=0):
        """Yields lines from start_pos"""

        self.mmfile.seek(start_pos, os.SEEK_SET)

        while True:
            data = self.mmfile.readline()
            if data == '':
                break

            # eliminate trailing \n, \r
            data = data[:-1]
            if len(data) > 0 and data[-1] == '\r':
                data = data[:-1]

            data = data.split('\r')
            for line in data:
                yield line

    def _strip_comment(self, data):
        """Strips comments."""

        ix = data.find('%')
        if ix == -1:
            return data

        return data[:ix]


    def get_xref_pos(self):
        """Get the position of the first cross reference table.

        Returns:
            An integer denoting the position of the first cross
                reference table. If error, 0 is returned.

        """

        ret = 0
        prev_line = None

        for line in self._reverse_lines():
            if line == '':
                continue
            elif line == 'startxref':
                break

            prev_line = line

        if prev_line is None:
            logger.error('Can not find startxref')
            return ret

        prev_line = self._strip_comment(prev_line)

        if prev_line.isdigit():
            ret = int(prev_line)
            logger.debug('startxref = %s', ret)

        return ret