#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


class BitWriterError(Exception): pass


class BitWriter(object):
    """A utility class to write value bits by bits.

    Attributes:
        data: The stream ob bits.
        last_byte: The last byte of the stream.
        bit_ptr: The bit pointer to last byte. (from 0 to 7)

    """

    def __init__(self):

        self.data = []
        self.last_byte = None
        self.bit_ptr = 0

    def write(self, data, bit_length):
        """Write `data` as a `bit_length`-bit long data.

        Args:
            data: An integer to be written into stream.
            bit_length: An integer representing the bit length of data.

        Returns:
            BitWriter itself.

        """

        if bit_length <= 0 or (1 << bit_length) <= data:
            raise BitWriterError('invalid bit length: %s', bit_length)

        if bit_length == 8 and self.last_byte is None and self.bit_ptr == 0:
            self.data.append(chr(data))
            return self

        while bit_length > 0:

            remaining_bits = 8 - self.bit_ptr

            if self.last_byte is None:
                self.last_byte = 0

            if bit_length >= remaining_bits:
                bit_length -= remaining_bits

                self.last_byte |= ((data >> bit_length) & \
                                   ((1 << remaining_bits) - 1))

                data &= ((1 << bit_length) - 1)
                self.data.append(chr(self.last_byte))
                self.last_byte = None
                self.bit_ptr = 0
            else:
                self.last_byte |= ((data & ((1 << bit_length) - 1)) << \
                                   (remaining_bits - bit_length))
                self.bit_ptr += bit_length

                if self.bit_ptr == 8:
                    self.data.append(chr(self.last_byte))
                    self.last_byte = None
                    self.bit_ptr = 0

                break

        return self

    def __len__(self):
        """Returns bit length of data."""

        return len(self.data) * 8 + self.bit_ptr

    def flush(self):
        """Flush the stream."""

        if self.last_byte is not None:
            self.data.append(chr(self.last_byte))

        self.last_byte = None
        self.bit_ptr = 0

        return self

    def __str__(self):
        """Output the stream."""

        return ''.join(self.data)
