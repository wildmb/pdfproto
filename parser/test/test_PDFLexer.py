# standard library imports
from contextlib import closing
import json
import mmap
import random
from tempfile import NamedTemporaryFile

# third party related imports
import pytest

# local library imports
from ..PDFLexer import PDFLexer, PDFLexerError


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
                    numeric_object = p.get_number(len(leading))
                    assert numeric_object.data == test_data[key]
                    assert numeric_object.start_pos == len(leading)
                    assert numeric_object.end_pos == len(leading) + len(key)


        with closing(NamedTemporaryFile()) as f:
            f.write('abc5\r')
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                with pytest.raises(PDFLexerError):
                    numeric_object = p.get_number(0)

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
                f.write(self._rand_white_space() + self._rand_string(8))
                f.flush()

                with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                    p = PDFLexer(stream)
                    string_object = p.get_literal_string(0)
                    assert string_object.data == expect_val
                    assert string_object.start_pos == 0
                    assert string_object.end_pos == len(content)

    def _rand_white_space(self):

        return random.choice('\0\t\n\f\r ')

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
            f.write(self._rand_white_space() + self._rand_string(8))
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                string_object = p.get_hexadecimal_string(0)
                assert string_object.data == test_data
                assert string_object.start_pos == 0
                assert string_object.end_pos == len(test_data) * 2 + 2

        # empty case
        with closing(NamedTemporaryFile()) as f:
            f.write('<>')
            f.write(self._rand_white_space() + self._rand_string(8))
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                string_object = p.get_hexadecimal_string(0)
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
            f.write(self._rand_white_space() + self._rand_string(8))
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                string_object = p.get_hexadecimal_string(0)
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
                f.write(self._rand_white_space() + self._rand_string(8))
                f.flush()

                with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                    p = PDFLexer(stream)
                    name_object = p.get_name(0)
                    assert name_object.data == expect_val
                    assert name_object.start_pos == 0
                    assert name_object.end_pos == len(name)

    def test_get_indirect_reference(self):

        with closing(NamedTemporaryFile()) as f:
            obj_num = random.randint(1, 2**31 - 1)
            gen_num = random.randint(0, 65535)
            write_val = '%s %s R' % (obj_num, gen_num)
            f.write(write_val)
            f.write(self._rand_white_space() + self._rand_string(8))
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                indirect_ref = p.get_indirect_reference(0)
                assert indirect_ref.object_num == obj_num
                assert indirect_ref.generation_num == gen_num
                assert indirect_ref.start_pos == 0
                assert indirect_ref.end_pos == len(write_val)

    def _test_by_json_dump(self, pdf_json_str, real_json, isdict=True):

        with closing(NamedTemporaryFile()) as f:
            f.write(pdf_json_str)
            f.write(self._rand_white_space() + self._rand_string(8))
            f.flush()

            with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                p = PDFLexer(stream)
                d = p.get_dictionary(0) if isdict else p.get_array(0)
                assert json.dumps(d.data, sort_keys=True) == \
                       json.dumps(real_json, sort_keys=True)

    def testget_dictionary1(self):

        self._test_by_json_dump("<<>>", {})
        self._test_by_json_dump("<< >>", {})

    def testget_dictionary2(self):

        test_data = """<<
                            /Type /Example
                            /Subtype/DictionaryExample
                            /Version 0.01
                            /IntegerItem 12
                            /StringItem( a string )
                            /Subdictionary <</Item1 0.4
                                             /Item2 true
                                             /LastItem ( not ! )
                                             /VeryLastItem ( OK )
                                           >>
                            /IndirectRef 1 0 R
                            /False false
                            /NotExist null
                       >>"""
        test_data_dict = {
                'Type': 'Example', 'Subtype': 'DictionaryExample',
                'Version': 0.01, 'IntegerItem': 12,
                'StringItem': ' a string ',
                'Subdictionary': {
                    'Item1': 0.4, 'Item2': True,
                    'LastItem': ' not ! ', 'VeryLastItem': ' OK '
                },
                'IndirectRef': [1, 0],
                'False': False,
                'NotExist': None,
        }

        self._test_by_json_dump(test_data, test_data_dict)

    def test_get_array1(self):

        self._test_by_json_dump("[]", [], False)
        self._test_by_json_dump("[ ]", [], False)

    def test_get_array2(self):

        self._test_by_json_dump("[ 549 3.14 false (Ralph) /SomeName ]",
                                [549, 3.14, False, 'Ralph', 'SomeName'], False)
        self._test_by_json_dump("[1 2 3 4 5 6 R]", [1, 2, 3, 4, [5, 6]], False)

    def test_get_array3(self):

        self._test_by_json_dump("[[[[1]]]]", [[[[1]]]], False)

    def test_get_indirect_object(self):

        test_data = (
                ("""1 0 obj
                    123
                    endobj""", 1, 0, 123),
                ("""2 0 obj
                    -0.1
                    endobj""", 2, 0, -0.1),
                ("""3 0 obj
                    (billing)
                    endobj""", 3, 0, 'billing'),
                ("""4 0 obj
                    <62696c6c696e67>
                    endobj""", 4, 0, 'billing'),
                ("""5 0 obj
                    /billing
                    endobj""", 5, 0, 'billing'),
                ("""6 0 obj
                    <</a/billing /b 123
                      /c true /d [ 1 2 3 ]
                      /e (billing) /f<62696c6c696e67>
                      /g null /h<<>>>>
                    endobj""", 6, 0,
                 {'a': 'billing', 'b': 123, 'c': True, 'd': [1, 2, 3],
                  'e': 'billing', 'f': 'billing', 'g': None,
                  'h': {}}),
                ("""7 0 obj [/a /b 1 2 3 0 R] endobj""", 7, 0, ['a', 'b', 1, 2, [3, 0]]),
        )

        for test_str, obj_num, gen_num, data in test_data:
            with closing(NamedTemporaryFile()) as f:
                f.write(test_str)
                f.write(self._rand_white_space() + self._rand_string(8))
                f.flush()

                with closing(mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)) as stream:
                    p = PDFLexer(stream)
                    io = p.get_indirect_object(0)
                    assert io.object_num == obj_num
                    assert io.genration_num == gen_num
                    assert io.start_pos == 0
                    assert io.end_pos == len(test_str)
                    assert json.dumps(io.data.data, sort_keys=True) == \
                           json.dumps(data, sort_keys=True)
