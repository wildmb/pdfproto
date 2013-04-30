#!/usr/bin/env python

def filter_factory(filter_name, *args):
    """Instantiate a filter instance."""

    if filter_name == 'ASCIIHexDecode':
        from pdfproto.filters.ASCIIHexDecoder import ASCIIHexDecoder
        return ASCIIHexDecoder()
    elif filter_name == 'ASCII85Decode':
        from pdfproto.filters.ASCII85Decoder import ASCII85Decoder
        return ASCII85Decoder()
    elif filter_name == 'LZWDecode':
        from pdfproto.filters.LZWDecoder import LZWDecoder
        return LZWDecoder()
    elif filter_name == 'FlateDecode':
        from pdfproto.filters.FlateDecoder import FlateDecoder
        return FlateDecoder()
    elif filter_name == 'RunLengthDecode':
        from pdfproto.filters.RunLengthDecoder import RunLengthDecoder
        return RunLengthDecoder()
    elif filter_name == 'CCITTFaxDecode':
        raise NotImplementedError()
    elif filter_name == 'JBIG2Decode':
        raise NotImplementedError()
    elif filter_name == 'DCTDecode':
        raise NotImplementedError()
    elif filter_name == 'JPXDecode':
        raise NotImplementedError()
    elif filter_name == 'Crypt':
        raise NotImplementedError()

    raise KeyError('unknown filter_name: %s', filter_name)

