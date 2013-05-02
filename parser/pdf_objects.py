#!/usr/bin/env python

# standard library import

# third party related import

# local library import
from pdfproto.filters import filter_factory


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


class PDFNumericObject(PDFBaseObject):
    """PDF Numeric Objects

    PDF provides 2 types of numeric objects: integer and real.

    Attributes:
        data: An integer or a float.

    """

    def __init__(self):
        super(PDFNumericObject, self).__init__()


class PDFStringObject(PDFBaseObject):
    """PDF String Objects

    Attributes:
        data: A series of zero or more bytes.

    """

    def __init__(self):
        super(PDFStringObject, self).__init__()


class PDFNameObject(PDFBaseObject):
    """PDF Name Object

    A uniquely defined atomic symbol.

    Attributes:
        data: A sequence of characters.

    """

    def __init__(self):
        super(PDFNameObject, self).__init__()


class PDFDictObject(PDFBaseObject):
    """PDF Dictionary Object

    Attributes:
        data: A dict: { string: PDFBaseObject.data }

    """

    def __init__(self):
        super(PDFDictObject, self).__init__()
        self.data = {}
        self.entries = []

    def add_entry(self, key, value):
        """Add an entry to the associative table.

        Args:
            key: Should be a PDFNameObject.
            value: May be any instance of PDFBaseObject.

        """

        self.entries.append((key, value))
        self.data[key.data] = value.data


class PDFArrayObject(PDFBaseObject):
    """PDF Array Object

    Attributes:
        data: An array [ PDFBaseObject.data ]

    """

    def __init__(self):
        super(PDFArrayObject, self).__init__()
        self.entries = []
        self.data = []

    def add_entry(self, value):
        """Add an entry to the array.

        Args:
            value: May be any instance of PDFBaseObject.

        """

        self.entries.append(value)
        self.data.append(value.data)


class PDFIndirectRefObject(PDFBaseObject):
    """PDF Indirect Object

    Attributes:
        data: [object_number, generation_number]
        object_num: An integer of the object number
        generation_num: An integer of the generation number.

    """

    def __init__(self):
        super(PDFIndirectRefObject, self).__init__()

    @property
    def object_num(self):
        return self.data[0]

    @property
    def generation_num(self):
        return self.data[1]


class PDFBooleanObject(PDFBaseObject):
    """PDF Boolean Object

    Attributes:
        data: True / False

    """

    def __init__(self):
        super(PDFBooleanObject, self).__init__()


class PDFNullObject(PDFBaseObject):
    """PDF Null Object

    Attributes:
        data: None

    """

    def __init__(self):
        super(PDFNullObject, self).__init__()


class PDFIndirectObject(PDFBaseObject):
    """PDF Indirect Object.

    Attributes:
        data: An instance of PDFBaseObject.
        object_num: An integer of the object number
        generation_num: An integer of the generation number.

    """

    def __init__(self):
        super(PDFIndirectObject, self).__init__()
        self.object_num = 0
        self.generation_num = 0


class PDFStreamObject(PDFBaseObject):
    """PDF Stream Object

    Attributes:
        data: A sequence of zero ob more bytes.
        raw_data: A sequence of bytes. (may be compressed)
        stream_dict: An instance of PDFDictObject.

    """

    def __init__(self):
        super(PDFStreamObject, self).__init__()
        self.stream_dict = None
        self.raw_data = None

    def decode(self):

        if self.raw_data is None:
            return self.data

        stream_dict = self.stream_dict.data

        filters = self._get_filters()
        decode_params = self._get_decode_params()

        decoded = self.raw_data

        for f, param in zip(filters, decode_params):
            pdf_filter = filter_factory(f, **param)
            decoded = pdf_filter.decode(decoded)

        self.data = decoded
        self.raw_data = None

        return decoded

    def get_decoded_data(self):

        if self.raw_data is not None:
            return self.decode()

        return self.data

    def _get_filters(self):

        stream_dict = self.stream_dict.data

        filters = stream_dict.get('Filter', [])
        if not isinstance(filters, list):
            filters = [filters]

        return filters

    def _get_decode_params(self):

        stream_dict = self.stream_dict.data

        decode_params = stream_dict.get('DecodeParms', [])
        if not isinstance(filter, list):
            decode_params = [decode_params]

        return decode_params
