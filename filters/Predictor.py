#!/usr/bin/env python

# standard library imports
import logging as logger

# third party related imports

# local library imports


class PredictorError(Exception): pass


class Predictor:

    NONE = 1
    TIFF = 2
    PNG_NONE = 10
    PNG_SUB = 11
    PNG_UP = 12
    PNG_AVERAGE = 13
    PNG_PAETH = 14
    PNG_OPTIMUM = 15

    @classmethod
    def post_predict(cls, data, predictor=Predictor.NONE, colors=1,
                     bits_per_component=8, columns=1):
        """Apply predictor algorithm after filter decode data.

        Args:
            data: A sequence of bytes that filter decoded.
            predictor: An integer indicating the predictor algorithm.
            colors: The number of interleaved color components per
                sample.
            bits_per_component: The number of bits used to represent
                each color component in a sample.
            columns: The number of sample in each row.

        Returns:
            A sequence of bytes.

        """

        if predictor == self.NONE:
            return data

        if colors not in xrange(1, 5):
            raise PredictorError('colors should be between 1 and 4')

        if bits_per_component not in (1, 2, 4, 8, 16):
            raise PredictorError('bits_per_component should be in 1, 2, 4, 8, 16')

        comp_per_line = columns * colors
        bytes_per_px = (colors * bits_per_component + 7) / 8
        # TODO why + 1?
        bytes_per_row = (comp_per_line * bits_per_component + 7) / 8 + 1

        if predictor == cls.TIFF:
            return cls._tiff_post_predict(data, colors, bits_per_component, columns)
        elif predictor >= cls.PNG_NONE:
            return cls._png_post_predict(data, bytes_per_px, bytes_per_row)

        raise PredictorError('unknown predictor: %s', predictor)

    @classmethod
    def _png_post_predict(cls, data, bytes_per_px, bytes_per_row):

        result = []
        up_row = ['\0'] * bytes_per_row
        this_row = ['\0'] * bytes_per_row
        num_row = (len(data) + bytes_per_row - 1) / bytes_per_row

        for row in xrange(num_row):
            ix = row * bytes_per_row
            line = data[ix:(ix + bytes_per_row)]
            predictor = 10 + ord(line[0])
            line[0] = '\0'

            for i in xrange(1, len(line)):
                up = ord(up_row[i])
                if bytes_per_px > i:
                    left = up_left = 0
                else:
                    left = ord(line[i - bytes_per_px])
                    up_left = ord(up_row[i - bytes_per_px])

                if predictor == cls.PNG_NONE:
                    this_row = line
                    break
                elif predictor == cls.PNG_SUB:
                    this_row[i] = chr((ord(line[i]) + left) & 0xFF)
                elif predictor == cls.PNG_UP:
                    this_row[i] = chr((ord(line[i]) + up) & 0xFF)
                elif predictor == cls.PNG_AVERAGE:
                    this_row[i] = chr((ord(line[i]) + (left + up) / 2) & 0xFF)
                elif predictor == cls.PNG_PAETH:
                    p = left + up - up_left
                    pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                    pp = min(zip((pa, pb, pc), (left, up, up_left)))[1]
                    this_row[i] = chr((ord(line[i]) + pp) & 0xFF)
                else:
                    logger.warn('unknown PNG predictor: %s', predictor)
                    this_row = line
                    break

            result.append(this_row)
            up_row = this_row

        return ''.join(this_row)

    @classmethod
    def _tiff_post_predict(cls, data, colors, bits_per_component, columns):

        bytes_per_row = (colors * bits_per_component * columns + 7) / 8
        num_row = len(data) / bytes_per_row

