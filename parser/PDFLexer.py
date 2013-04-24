#!/usr/bin/env python

# standard library import
import logging as logger
import os
import re

# third party related import

# local library import

class PDFLexerError(Exception): pass


class PDFBaseObject(object):
    """A base class for PDF 8 basic types of objects.

    Attribute:
        start_pos: An integer indicating the starting position of the
            data.
        end_pos: An integer indicating the end position (not included)
            of the data.
        data: Transformed python object.

    """

    def __init__(self):
        self.start_pos = 0
        self.end_pos = 0
        self.data = None


class PDFNumericObject(PDFBaseObject): pass


class PDFStringObject(PDFBaseObject): pass


class PDFNameObject(PDFBaseObject): pass


class PDFDictObject(PDFBaseObject):

    def __init__(self):
        super(PDFDictObject, self).__init__()
        self.data = {}
        self.entries = []

    def add_entry(self, key, value):

        self.entries.append((key, value))
        self.data[key.data] = value.data


class PDFArrayObject(PDFBaseObject):

    def __init__(self):
        super(PDFArrayObject, self).__init__()
        self.entries = []
        self.data = []

    def add_entry(self, value):

        self.entries.append(value)
        self.data.append(value.data)


class PDFIndirectRefObject(PDFBaseObject):

    @property
    def object_num(self):
        return self.data[0]

    @property
    def generation_num(self):
        return self.data[1]


class PDFBooleanObject(PDFBaseObject): pass


class PDFNullObject(PDFBaseObject): pass


class PDFLexer:
    """

    PDFLexer is aim to return the 8 basic primitive object in PDF
    binary content.

    Attribute:
        stream: A memory mapped file.

    """

    WHITE_SPACE_CHARCTERS = '\0\t\n\f\r '

    DELIMITER_CHARACTERS = '()<>[]{}/%'

    NUMERIC_CHARACTERS = '0123456789+-.'

    RE_WHITE_SPACE = re.compile(r'[\0\t\n\f\r ]')

    # 7.3.4.2
    # Ab EOL marker appearing within a literal string without a
    # preceding REVERSE SOLIDUS shall be treated as a byte value of
    # (0Ah), irrespective of whether the EOL marker was a CARRIAGE
    # RETURN (0Dh), a LINE FEED (0Ah), or both
    RE_EOL_WO_PRECEDING_SOLIDUS = re.compile(r'((?<=[^\\])[\n\r]+|^[\n\r]+)')

    RE_OCTAL_ESCAPE = re.compile(r'\\[0-7]{1,3}')

    RE_NUMBER_SIGN_ESCAPE = re.compile(r'#[0-9a-fA-F]{2}')

    def __init__(self, stream):

        self.stream = stream
        self.max_pos = self.stream.size()

    def get_obj(self, pos=None):

        ch, stream_pos = self._get_single_byte(pos)

        if ch in self.NUMERIC_CHARACTERS:
            if ch.isdigit():
                try:
                    return self._get_indirect_reference(stream_pos)
                except PDFLexerError:
                    pass

            return self._get_number(stream_pos)
        elif ch == '(':
            return self._get_literal_string(stream_pos)
        elif ch == '/':
            return self._get_name(stream_pos)
        elif ch == '[':
            return self._get_array(stream_pos)
        elif ch == '<':
            next_char, next_char_pos = self._get_single_byte(stream_pos + 1)
            if next_char == '<' and next_char_pos == stream_pos + 1:
                return self._get_dictionary(stream_pos)

            return self._get_hexadecimal_string(stream_pos)
        elif ch == 't':
            b = self.stream[stream_pos:min(self.max_pos, stream_pos + 4)]
            if b == 'true':
                ret = PDFBooleanObject()
                ret.start_pos, ret.end_pos = stream_pos, stream_pos + 4
                ret.data = True
                return ret
        elif ch == 'f':
            b = self.stream[stream_pos:min(self.max_pos, stream_pos + 5)]
            if b == 'false':
                ret = PDFBooleanObject()
                ret.start_pos, ret.end_pos = stream_pos, stream_pos + 5
                ret.data = False
                return ret
        elif ch == 'n':
            b = self.stream[stream_pos:min(self.max_pos, stream_pos + 4)]
            if b == 'null':
                ret = PDFNullObject()
                ret.start_pos, ret.end_pos = stream_pos, stream_pos + 4
                ret.data = None
                return ret

        return None

    def _get_single_byte(self, stream_pos):
        """Get a meaningful character. Skip comment and white space."""

        ch, pos = None, stream_pos

        while pos < self.max_pos:
            ch = self.stream[pos]

            if ch == '%':
                pos = self._skip_comment(pos)
                continue

            if self._is_white_space(ch):
                pos += 1
                continue

            break

        return (ch, pos)

    def _is_white_space(self, ch):
        """Test if it is a white-space character."""

        return ch in self.WHITE_SPACE_CHARCTERS

    def _skip_comment(self, stream_pos):
        """Try to skip comment and get the position of next object."""

        assert(self.stream[stream_pos] == '%')

        pos = stream_pos

        while pos < self.max_pos:
            if self.stream[pos] in ('\r', '\n'):
                break

            pos += 1

        return pos

    def _get_number(self, stream_pos):
        """Try to get a int or float number at stream_pos."""

        ret = PDFNumericObject()
        ret.start_pos = ret.end_pos = stream_pos

        while ret.end_pos < self.max_pos:
            if self.stream[ret.end_pos] not in self.NUMERIC_CHARACTERS:
                break

            ret.end_pos += 1

        data = self.stream[ret.start_pos:ret.end_pos]

        try:
            ret.data = float(data) if '.' in data else int(data)
        except (ValueError,), e:
            logger.error('Invalid numeric object: %s', data)
            raise PDFLexerError(unicode(e))

        return ret

    def _octal_replacer(self, match_obj):
        """It is used in re.sub and will replace octal code to character."""

        return chr(int(match_obj.group(0)[1:], 8))

    def _number_sign_replacer(self, match_obj):
        """
        It is used in re.sub and will replace number sign escape
        characters.

        """

        return chr(int(match_obj.group(0)[1:], 16))

    def _get_literal_string(self, stream_pos):
        """Try to get a string at stream_pos."""

        assert(self.stream[stream_pos] == '(')

        ret = PDFStringObject()
        ret.start_pos = stream_pos
        ret.end_pos = stream_pos + 1

        num_parentheses = 1
        string_data = []

        # retrieve a complete literal string based on balanced
        # parentheses
        while ret.end_pos < self.max_pos:
            ch = self.stream[ret.end_pos]

            if ch == '(':
                if  (len(string_data) == 0) or \
                    (len(string_data) > 0 and string_data[-1] != '\\'):
                    num_parentheses += 1
            elif ch == ')':
                # if two reverse solidus are before, then it won't be
                # treated as escape
                if len(string_data) > 0 and string_data[-1] == '\\':
                    if len(string_data) > 1 and string_data[-2] == '\\':
                        num_parentheses -= 1
                else:
                    num_parentheses -= 1

            if num_parentheses == 0:
                break

            string_data.append(ch)
            ret.end_pos += 1

        if self.stream[ret.end_pos] != ')':
            logger.error('Unterminated literal string')
            raise PDFLexerError('Unterminated literal string')

        ret.end_pos += 1
        literal_str = ''.join(string_data)

        # An EOL marker appearing within a literal string without a
        # preceding REVERSE SOLIDUS shall be treated as a byte value of
        # (0Ah), irrespective of whether the EOL marker was a CARRIAGE
        # RETURN (0Dh), a LINE FEED (0Ah), or both
        literal_str = self.RE_EOL_WO_PRECEDING_SOLIDUS.sub('\n', literal_str)

        # deal with escape strings
        escape_table = (
            # disregard the REVERSE SOLIDUS and the EOL marker following it
            ('\\\n', ''), ('\\\r', ''), ('\\\r\n', ''),
            # 7.3.4.2 Table 3
            ('\\n', '\n'), ('\\r', '\r'), ('\\t', '\t'), ('\\b', '\b'),
            ('\\f', '\f'), ('\\(', '('), ('\\)', ')'), ('\\\\', '\\')
        )
        for replacee, replacer in escape_table:
            literal_str = literal_str.replace(replacee, replacer)

        # deal with octal codes
        ret.data = self.RE_OCTAL_ESCAPE.sub(self._octal_replacer, literal_str)

        return ret

    def _get_hexadecimal_string(self, stream_pos):
        """Try to get a string at stream_pos."""

        assert(self.stream[stream_pos] == '<')

        ret = PDFStringObject()
        ret.start_pos = ret.end_pos = stream_pos
        ret.data = []

        # retrieve a complete hexadecimal string
        while ret.end_pos < self.max_pos:
            if self.stream[ret.end_pos] == '>':
                break

            ret.end_pos += 1

        if self.stream[ret.end_pos] != '>':
            logger.error('Unterminated hexadecimal string')
            raise PDFLexerError('Unterminated hexadecimal string')

        hex_str = self.stream[(ret.start_pos + 1):ret.end_pos]

        # 7.3.4.3
        # White-space characters shall be ignored
        hex_str = self.RE_WHITE_SPACE.sub('', hex_str)

        # If there is an odd number of digits, the final digit shall be
        # assumed to be 0
        if len(hex_str) % 2 == 1:
            hex_str = ''.join((hex_str, '0'))

        for i in xrange(0, len(hex_str), 2):
            ret.data.append(chr(int(hex_str[i:(i + 2)], 16)))

        ret.end_pos += 1
        ret.data = ''.join(ret.data)

        return ret

    def _get_name(self, stream_pos):
        """Try to get a name object at stram_pos."""

        assert(self.stream[stream_pos] == '/')

        ret = PDFNameObject()
        ret.start_pos = stream_pos
        ret.end_pos = stream_pos + 1

        # retrieve a complete name
        while ret.end_pos < self.max_pos:
            if  self.stream[ret.end_pos] in self.WHITE_SPACE_CHARCTERS or \
                self.stream[ret.end_pos] in self.DELIMITER_CHARACTERS:
                break

            ret.end_pos += 1

        name = self.stream[(ret.start_pos + 1):ret.end_pos]
        name = self.RE_NUMBER_SIGN_ESCAPE.sub(self._number_sign_replacer, name)
        ret.data = name

        return ret

    def _get_indirect_reference(self, stream_pos):
        """Try to get an indirect reference at stream_pos."""

        assert(self.stream[stream_pos].isdigit())

        try:
            object_num = self._get_number(stream_pos)
            if not isinstance(object_num.data, int):
                raise PDFLexerError()
        except PDFLexerError, e:
            raise PDFLexerError('Invalid indirect reference(object number)')

        try:
            generation_num = self._get_number(object_num.end_pos + 1)
            if not isinstance(generation_num.data, int):
                raise PDFLexerError()
        except PDFLexerError, e:
            raise PDFLexerError('Invalid indirect reference(generation number')

        if self.stream[min(self.max_pos, generation_num.end_pos + 1)] != 'R':
            raise PDFLexerError('Invalid indirect reference')

        ret = PDFIndirectRefObject()
        ret.start_pos = stream_pos
        ret.end_pos = generation_num.end_pos + 1 + 1
        ret.data = (object_num.data, generation_num.data)

        return ret

    def _get_dictionary(self, stream_pos):
        """Try to get a dictionary object at stream_pos."""

        assert(self.stream[stream_pos] == '<')
        assert(self.stream[stream_pos + 1] == '<')

        ret = PDFDictObject()
        ret.start_pos = stream_pos
        ret.end_pos = stream_pos + 2

        while True:
            # parse dictionary key
            ch, ch_pos = self._get_single_byte(ret.end_pos)

            if ch == '>':
                if self.stream[ch_pos + 1] != '>':
                    raise PDFLexerError('unbalanced dictionary enclose')
                ret.end_pos = ch_pos + 2
                break
            elif ch == '/':
                key = self._get_name(ch_pos)
                ret.end_pos = key.end_pos + 1
            else:
                raise PDFLexerError('parse dictionary error')

            # parse dictionary value
            value = self.get_obj(ret.end_pos)
            ret.add_entry(key, value)
            ret.end_pos = value.end_pos

        return ret

    def _get_array(self, stream_pos):
        """Try to get an array object at stream_pos."""

        assert(self.stream[stream_pos] == '[')

        ret = PDFArrayObject()
        ret.start_pos = stream_pos
        ret.end_pos = stream_pos + 1

        while True:
            value = self.get_obj(ret.end_pos)
            if value is None:
                ch, ch_pos = self._get_single_byte(ret.end_pos)
                if ch == ']':
                    ret.end_pos = ch_pos + 1
                    break

                raise PDFLexerError('parse array error')

            ret.add_entry(value)
            ret.end_pos = value.end_pos + 1

        return ret
