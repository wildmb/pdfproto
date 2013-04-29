#!/usr/bin/env python

# standard library import
import logging as logger

# third party related import

# local library import


class PDFCrossRefSectionError(Exception): pass


class PDFCrossRefSection:

    def __init__(self):

        self.offset_dict = {}

        # TODO: maybe we don't need this
        self.free_dict = {}

    def load_section(self, parser, xref_pos):
        """Load cross reference section

        Args:
            parser: An instance of PDFParser
            xref_pos: An integer that cross reference table starts.

        """

        # test the 1st line must be keyword "xref"
        for line in parser.next_lines(xref_pos):
            if line != 'xref':
                logger.error('Should be keyword xref')
                raise PDFCrossRefTableError('Should be keyword xref')

            break

        obj_num, num_remaining = 0, 0

        for line in parser.next_lines(xref_pos + 5):
            line = line.strip()
            if line == '':
                continue

            if num_remaining == 0:
                obj_num, num_remaining = self._get_subsection_header(line)
                if obj_num is None:
                    # reach the end of cross-reference table
                    break

                continue

            offset, gen_num, isused = self._get_subsection_body(line)
            if offset is None:
                logger.error('Invalid cross referrence subsection')
                raise PDFCrossRefSectionError()

            self.offset_dict[(obj_num, gen_num)] = offset
            self.free_dict[(obj_num, gen_num)] = isused

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
            isused = entry[2] == 'n'
        except (TypeError, ValueError), e:
            logger.exception(e)
            raise PDFCrossRefSectionError('Should be nnnnnnnnnn ggggg n/f')

        return offset, generation_num, isused
