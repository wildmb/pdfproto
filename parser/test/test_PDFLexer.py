# standard library imports
from contextlib import closing
import mmap
import random
from tempfile import NamedTemporaryFile

# third party related imports
import pytest

# local library imports
from ..PDFLexer import PDFLexer, PDFLexerError, PDFNumericObject


class TestPDFLexer:

    def test_get_number(self):

        test_data = {
            '123': 123, '43445': 43445, '+17': 17, '-98': -98,
            '34.5': 34.5, '-3.62': -3.62, '+123.6': 123.6, '4.': 4.0,
            '-0.002': -0.002, '0.0': 0,
        }

        for key in test_data:
            with closing(NamedTemporaryFile()) as f:
                leading = map(lambda i: random.randint(0, 255),
                              xrange(random.randint(0, 255)))

                f.write(bytearray(leading))
                f.write(key)
                f.write(random.choice((' ', '\r', '\n')))
                f.flush()

                with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                    p = PDFLexer(stream)
                    numeric_object = p._get_number(len(leading))
                    assert numeric_object.data == test_data[key]
                    assert numeric_object.start_pos == len(leading)
                    assert numeric_object.end_pos == len(leading) + len(key)


        with closing(NamedTemporaryFile()) as f:
            f.write('abc5\r')
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                with pytest.raises(PDFLexerError):
                    numeric_object = p._get_number(0)

    def test_get_literal_string(self):

        test_data = (
            ('This is a string', 'This is a string'),
            ('Strings may contain newlines\nand such.',
             'Strings may contain newlines\nand such.'),
            ('Strings may contain balanced parentheses ()',
             'Strings may contain balanced parentheses ()'),
            ('Strings may contain special characters (*!&}^% and so on).',
             'Strings may contain special characters (*!&}^% and so on).'),
            ('', ''),
            ('It has zero (0) length.', 'It has zero (0) length.'),
            ('These \\ntwo strings \\nare\\n the same.',
             'These \ntwo strings \nare\n the same.'),
            ('This string has an end-of-line at the end of it.\n',
             'This string has an end-of-line at the end of it.\n'),
            ('So does this one.\\n', 'So does this one.\n'),
            ('The string contains \\245two octal characters\\307.',
             'The string contains \245two octal characters\307.'),
            ('\n\n\n', '\n'),
            ('\r\r\r', '\n'),
            ('\r\n\r\n', '\n'),
            ('\\n\\r\\t\\b\\f\\(\\)\\\\', '\n\r\t\b\f()\\')
        )

        for (literal, expect_val) in test_data:
            with closing(NamedTemporaryFile()) as f:
                content = ''.join(('(', literal, ')'))
                f.write(bytearray(content))
                f.flush()

                with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                    p = PDFLexer(stream)
                    string_object = p._get_literal_string(0)
                    assert string_object.data == expect_val
                    assert string_object.start_pos == 0
                    assert string_object.end_pos == len(content)

    def _rand_string(self, length):

        return ''.join(map(lambda i: chr(random.randint(0, 255)), xrange(length)))

    def _to_hex_notation(self, ch):

        ret = hex(ord(ch))[2:]
        if len(ret) == 1:
            return '0' + ret

        return ret

    def test_get_hexadecimal_string(self):

        # normal case
        test_data = self._rand_string(random.randint(0, 255))
        hex_str = ''.join(map(self._to_hex_notation, test_data))
        with closing(NamedTemporaryFile()) as f:
            f.write('<%s>' % hex_str)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                string_object = p._get_hexadecimal_string(0)
                assert string_object.data == test_data
                assert string_object.start_pos == 0
                assert string_object.end_pos == len(test_data) * 2 + 2

        # empty case
        with closing(NamedTemporaryFile()) as f:
            f.write('<>')
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                string_object = p._get_hexadecimal_string(0)
                assert string_object.data == ''
                assert string_object.start_pos == 0
                assert string_object.end_pos == 2

        # interleave white space characters
        test_data = self._rand_string(random.randint(0, 255))
        hex_str = ''.join(map(self._to_hex_notation, test_data))
        prob = 0.1
        hexs = []
        for i in xrange(len(hex_str)):
            while random.random() <= prob:
                hexs.append(random.choice((' ', '\n', '\r', '\t')))
            hexs.append(hex_str[i])
        hex_str = ''.join(hexs)

        with closing(NamedTemporaryFile()) as f:
            f.write('<%s>' % hex_str)
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                string_object = p._get_hexadecimal_string(0)
                assert string_object.data == test_data
                assert string_object.start_pos == 0
                assert string_object.end_pos == len(hex_str) + 2

    def test_get_name(self):

        test_data = (
            ('/Name1', 'Name1'),
            ('/ASomewhatLongerName', 'ASomewhatLongerName'),
            ('/A;Name_With-Various***Characters?',
             'A;Name_With-Various***Characters?'),
            ('/1.2', '1.2'),
            ('/$$', '$$'),
            ('/@pattern', '@pattern'),
            ('/.notdef', '.notdef'),
            ('/lime#20Green', 'lime Green'),
            ('/paired#28#29parentheses', 'paired()parentheses'),
            ('/The_Key_of_F#23_Minor', 'The_Key_of_F#_Minor'),
            ('/A#42', 'AB')
        )

        for name, expect_val in test_data:
            with closing(NamedTemporaryFile()) as f:
                f.write(name)
                f.flush()

                with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                    p = PDFLexer(stream)
                    name_object = p._get_name(0)
                    assert name_object.data == expect_val