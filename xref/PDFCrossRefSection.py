#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import
from pdfproto.parser.PDFLexer import PDFLexerError
from pdfproto.trailer.PDFTrailer import PDFTrailer


class PDFCrossRefSectionError(Exception): pass


class PDFCrossRefSection:
    """

    Attributes:
        offset_dict: A dict maps (object_num, generation_num) -> int
        free_dict: A dict maps (object_num, generation_num) -> bool
        trailer: An instance of PDFTrailer

    """

    def __init__(self):

        self.offset_dict = {}

        # TODO: maybe we don't need this
        self.free_dict = {}

        self.trailer = None

    def load_section(self, parser, xref_pos):
        """Load cross reference section

        Args:
            parser: An instance of PDFParser
            xref_pos: An integer that cross reference table starts.

        """

        # test the 1st line must be keyword "xref"
        for (line, pos) in parser.next_lines(xref_pos, ensure_pos=True):
            if line != 'xref':
                logger.error('Should be keyword xref')
                raise PDFCrossRefSectionError('Should be keyword xref')

            break

        obj_num, num_remaining = 0, 0

        for (line, pos) in parser.next_lines(xref_pos + 5, ensure_pos=True):
            line = line.strip()
            if line == '':
                continue

            if num_remaining == 0:
                if line == 'trailer':
                    self._load_trailer(parser, pos)
                    break

                obj_num, num_remaining = self._get_subsection_header(line)
                if obj_num is None:
                    logger.error('...%s...', parser.stream[pos:(pos + 10)])
                    logger.error('Invalid cross reference subsection')
                    raise PDFCrossRefSectionError()

                continue

            offset, gen_num, isfree = self._get_subsection_body(line)
            if offset is None:
                logger.error('Invalid cross referrence subsection')
                raise PDFCrossRefSectionError()

            self.offset_dict[(obj_num, gen_num)] = offset
            self.free_dict[(obj_num, gen_num)] = isfree

            obj_num += 1
            num_remaining -= 1

    def _get_subsection_header(self, entry):

        entry = entry.strip().split(' ')

        if len(entry) != 2:
            return None, None

        try:
            init_obj_num = int(entry[0])
            num_obj = int(entry[1])
        except (ValueError, TypeError), e:
            logger.exception(e)
            raise PDFCrossRefSectionError('Should be two integers')

        return init_obj_num, num_obj

    def _get_subsection_body(self, entry):

        entry = entry.strip().split(' ')

        if len(entry) != 3:
            return None, None, None

        try:
            offset = int(entry[0])
            generation_num = int(entry[1])
            isfree = (entry[2] == 'f')
        except (TypeError, ValueError), e:
            logger.exception(e)
            raise PDFCrossRefSectionError('Should be nnnnnnnnnn ggggg n/f')

        return offset, generation_num, isfree

    def _load_trailer(self, parser, trailer_pos):
        """Create the PDFTrailer instance.

        Args:
            parser: An instance of PDFParser
            trailer_pos: The starting file position of trailer.

        """

        trailer_dict = None

        for (line, pos) in parser.next_lines(trailer_pos, ensure_pos=True):
            if line == '':
                continue

            try:
                trailer_dict = parser.lexer.get_dictionary(pos)
                break
            except PDFLexerError, e:
                continue

        if trailer_dict is None:
            return

        self.trailer = PDFTrailer(trailer_dict.data)

