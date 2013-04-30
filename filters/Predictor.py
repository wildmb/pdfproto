#!/usr/bin/env python

# standard library imports

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
    def post_predict(self, data, predictor=Predictor.NONE, colors=1,
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

        if predictor == self.TIFF:
            return self.tiff_post_predict(data, colors, bits_per_component, columns)
        elif predictor >= self.PNG_NONE:
            return self.png_post_predict(data, bytes_per_px, bytes_per_row)

        raise PredictorError('unknown predictor: %s', predictor)
