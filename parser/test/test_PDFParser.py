# standard library import
from contextlib import closing
import random
from tempfile import NamedTemporaryFile

# third party related import
import pytest

# local library import
from pdfproto.parser.PDFParser import *


class TestPDFParser:

    def test_open(self):

        # open a non-empty file
        with closing(NamedTemporaryFile()) as f:
            content = '1234'
            f.write(content)
            f.flush()

            p = PDFParser()
            p.open(f.name)

            assert p.stream[:] == content

    def test_get_header(self):

        for i in xrange(8):
            with closing(NamedTemporaryFile()) as f:
                header = '%%PDF-1.%s\r' % i
                f.write(header)
                f.flush()

                p = PDFParser()
                p.open(f.name)
                assert p.get_header() == header.strip()

            with closing(NamedTemporaryFile()) as f:
                header = '%%PDF-1.%s\n' % i
                f.write(header)
                f.flush()

                p = PDFParser()
                p.open(f.name)
                assert p.get_header() == header.strip()

            with closing(NamedTemporaryFile()) as f:
                header = '%%PDF-1.%s\r\n' % i
                f.write(header)
                f.flush()

                p = PDFParser()
                p.open(f.name)
                assert p.get_header() == header.strip()

        with closing(NamedTemporaryFile()) as f:
            f.write('1234\r')
            f.flush()

            with pytest.raises(PDFParserError):
                p = PDFParser()
                p.open(f.name)
                p.get_header()

        with closing(NamedTemporaryFile()) as f:
            f.write('%%PDF-1.8\r')
            f.flush()

            with pytest.raises(PDFParserError):
                p = PDFParser()
                p.open(f.name)
                p.get_header()

    def test_reverse_line(self):

        num_lines = random.randint(0, 10000)
        lines = []
        CR, LF = ord('\r'), ord('\n')

        for i in xrange(num_lines):
            num_bytes = self.rand_byte()
            bunch_bytes = map(lambda i: self.rand_byte(), xrange(num_bytes))
            bunch_bytes = filter(lambda b: b != CR and b != LF, bunch_bytes)
            lines.append(bytearray(bunch_bytes))

        with closing(NamedTemporaryFile()) as f:
            for ba in lines:
                eol = random.choice(('\r', '\n', '\r\n'))
                f.write(ba + eol)

            f.flush()

            p = PDFParser()
            p.open(f.name)

            output_lines = [line for line in p._reverse_lines()]
            output_lines = filter(lambda line: len(line) != 0, output_lines)
            output_lines.reverse()
            assert output_lines == filter(lambda line: len(line) != 0, lines)

    def test_next_lines(self):

        num_lines = random.randint(0, 10000)
        lines = []
        offset = 0

        CR, LF = ord('\r'), ord('\n')

        for i in xrange(num_lines):
            num_bytes = self.rand_byte()
            bunch_bytes = map(lambda i: self.rand_byte(), xrange(num_bytes))
            bunch_bytes = filter(lambda b: b != CR and b != LF, bunch_bytes)
            bunch_bytes = bytearray(bunch_bytes)
            bunch_bytes += bytearray(random.choice(('\r', '\n', '\r\n')))

            lines.append((bunch_bytes, offset))
            offset += len(bunch_bytes)

        with closing(NamedTemporaryFile()) as f:
            map(lambda li: f.write(li[0]), lines)
            f.flush()

            p = PDFParser()
            p.open(f.name)

            output_lines = [bytearray(line) for line in p.next_lines(skip_comment=False)]
            output_lines = filter(lambda line: len(line) != 0, output_lines)
            expect_lines = []
            for i in xrange(len(lines)):
                li = lines[i][0].replace('\r', '').replace('\n', '')
                if len(li) > 0 and li[-1] == '\r':
                    li = li[:-1]
                if len(li) > 0:
                    expect_lines.append(li)

            for ix, ol in enumerate(output_lines):
                assert ol == expect_lines[ix]

        with closing(NamedTemporaryFile()) as f:
            map(lambda li: f.write(li[0]), lines)
            f.flush()

            p = PDFParser()
            p.open(f.name)

            output_lines = [line for line in p.next_lines(ensure_pos=True, skip_comment=False)]
            output_lines = filter(lambda (line, offset): len(line) != 0, output_lines)
            expect_lines = []
            for i in xrange(len(lines)):
                li = lines[i][0].replace('\r', '').replace('\n', '')
                if len(li) > 0 and li[-1] == '\r':
                    li = li[:-1]
                if len(li) > 0:
                    expect_lines.append((li, lines[i][1]))

            for ix, ol in enumerate(output_lines):
                assert ol == expect_lines[ix]

    def rand_byte(self):
        """Get an integer 0 <= x <= 255"""

        return random.randint(0, 255)

    def test_get_xref_pos(self):

        with closing(NamedTemporaryFile()) as f:
            content = bytearray(0)
            for i in xrange(self.rand_byte()):
                content += bytearray(map(lambda i: self.rand_byte(),
                                         xrange(self.rand_byte())))

            content += '\rstartxref'
            for i in xrange(random.randint(1, 5)):
                content += random.choice(['\r', '\n', '\r\n'])

            pos = random.randint(0, 2**32 - 1)
            content += str(pos)
            content += '\r%%EOF'

            f.write(content)
            f.flush()

            p = PDFParser()
            p.open(f.name)
            assert p.get_xref_pos() == pos

