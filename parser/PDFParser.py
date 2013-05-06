#!/usr/bin/env python

# standard library import
from collections import deque
from contextlib import closing
import logging as logger
import mmap
import os

# third party related import

# local library import
from PDFLexer import PDFLexer
from pdfproto.xref.PDFCrossRefSection import PDFCrossRefSection
from pdfproto.xref.PDFCrossRefStream import PDFCrossRefStream


class PDFParserError(Exception): pass


class PDFParser:
    """

    PDFParser parses the binary content of pdf document.

    Attribute:
        stream: A memory mapped file, ie. the document.

    """

    def __init__(self):

        self._file_obj = None
        self.stream = None
        self.lexer = None

    def __del__(self):

        if self._file_obj is not None:
            self._file_obj.close()

        if self.stream is not None:
            self.stream.close()

    def open(self, name):
        """Open the specified pdf file.

        Args:
            name: A string denotes the pdf filename.

        """

        self._file_obj = open(name)
        self.stream = mmap.mmap(self._file_obj.fileno(), 0,
                                prot=mmap.PROT_READ)
        self.lexer = PDFLexer(self.stream)

    def get_header(self):
        """Get the header of the pdf file.

        Returns:
            A string representing the file header. Must be "%PDF-1.[0-7]"

        """

        if self.stream.tell() != 0:
            self.stream.seek(0, os.SEEK_SET)

        header = self.stream.readline().rstrip()

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
        self.stream.seek(0, os.SEEK_END)
        max_pos = self.stream.tell()
        end_pos = max_pos + 1

        while end_pos > 1:
            # find EOL
            carrage_ix = self.stream.rfind('\r', 0, end_pos)
            linefeed_ix = self.stream.rfind('\n', 0, end_pos)
            ix = max(carrage_ix, linefeed_ix)

            if ix == -1:
                yield self.stream[0:end_pos]
                break

            yield self.stream[min(ix + 1, max_pos):end_pos]

            curr_byte = self.stream[ix]
            if curr_byte == '\r':
                end_pos = ix
            else:
                if self.stream[max(0, ix - 1)] == '\r':
                    end_pos = ix - 1
                else:
                    end_pos = ix

    def next_lines(self, start_pos=0, ensure_pos=False, skip_comment=True):
        """Yields lines from start_pos

        Args:
            start_pos: An integer indicating where we start to split lines.
            ensure_pos: If true, return a tuple (line, starting_pos).
            skip_comment: If false, the comment will not be ignored.

        Returns:
            A stripped EOL string. If ensure_pos is True,
            (line, starting_pos) is yielded.

        """

        self.stream.seek(start_pos, os.SEEK_SET)
        prev_pos, curr_pos = start_pos, None

        while True:
            data = self.stream.readline()
            curr_pos = self.stream.tell()

            if data == '':
                break

            # eliminate trailing \n, \r
            data = data[:-1]
            if len(data) > 0 and data[-1] == '\r':
                data = data[:-1]

            # split by \r
            ix, pos = 0, 0
            while ix != -1:
                ix = data.find('\r', pos)

                line = data[pos:ix] if ix != -1 else data[pos:]

                if skip_comment:
                    comment_ix = line.find('%')
                    if comment_ix != -1:
                        line = data[pos:comment_ix]

                yield (line, prev_pos + pos) if ensure_pos else line

                pos = ix + 1

            prev_pos = curr_pos

    def _strip_comment(self, data):
        """Strips comments."""

        ix = data.find('%')
        return data if ix == -1 else data[:ix]

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

    def get_xref(self, xref_pos):
        """Get the cross reference tables.

        Args:
            xref_pos: The position of the latest updated trailer of the
                PDF.

        Returns:
            A list of instances of PDFCrossRefSection or
            PDFCrossRefStream which sorted by increment update order.

        """

        xref_queue = deque([xref_pos])
        ret = []

        while len(xref_queue) > 0:

            start_xref_pos = xref_queue.popleft()

            # fetch one single line
            for line in self.next_lines(start_xref_pos):
                break

            # determine cross reference type
            xref = PDFCrossRefSection() if line == 'xref' else PDFCrossRefStream()
            xref.parse(self, xref_pos)
            ret.append(xref)

            # ensure trailer is parsed as well
            if xref.trailer is None:
                logger.error('xref.trailer is None')
                raise PDFParserError('xref.trailer is None')

            # look up XRefStm
            if xref.trailer.xref_stream is not None:
                if not isinstance(xref.trailer.xref_stream, int):
                    logger.error('XRefStm should be an int')
                    raise PDFParserError('trailer.xref_stream should be an int')

                xref_queue.append(xref.trailer.xref_stream)

            # look up Prev
            if xref.trailer.prev is not None:
                if not isinstance(xref.trailer.prev, int):
                    logger.error('Prev should be an int')
                    raise PDFParserError('trailer.prev should be an int')

                xref_queue.append(xref.trailer.prev)

        return ret
