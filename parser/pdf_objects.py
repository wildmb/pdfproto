#!/usr/bin/env python

# standard library import

# third party related import

# local library import


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

    def __init__(self):
        super(PDFNumericObject, self).__init__()


class PDFStringObject(PDFBaseObject):

    def __init__(self):
        super(PDFStringObject, self).__init__()


class PDFNameObject(PDFBaseObject):

    def __init__(self):
        super(PDFNameObject, self).__init__()


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

    def __init__(self):
        super(PDFIndirectRefObject, self).__init__()

    @property
    def object_num(self):
        return self.data[0]

    @property
    def generation_num(self):
        return self.data[1]


class PDFBooleanObject(PDFBaseObject):

    def __init__(self):
        super(PDFBooleanObject, self).__init__()


class PDFNullObject(PDFBaseObject):

    def __init__(self):
        super(PDFNullObject, self).__init__()


class PDFIndirectObject(PDFBaseObject):

    def __init__(self):
        super(PDFIndirectObject, self).__init__()
        self.object_num = 0
        self.genration_num = 0


class PDFStreamObject(PDFBaseObject):

    def __init__(self):
        super(PDFStreamObject, self).__init__()
        self.stream_dict = {}
