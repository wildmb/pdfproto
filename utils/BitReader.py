#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


class BitReaderError(Exception): pass


class BitReader(object):
    """A utility class to read value bits by bits.

    Attributes:
        data: A sequence of bytes.
        byte_ptr: An integer indicating the current read pointer in
            byte (from 0 to len(data) - 1).
        bit_ptr: An integer indicating the current read pointer in bits
            (from 0 to 7).

    """

    def __init__(self, data):

        self.data = data
        self.byte_ptr = 0
        self.bit_ptr = 0
        self.reset()

    def reset(self):
        """Reset the pointer."""

        self.byte_ptr = self.bit_ptr = 0

    def iseod(self):
        """Whether or not the end of data is reached.

        Returns:
            True if end of data, otherwise false.

        """

        return self.byte_ptr >= len(self.data)

    @property
    def bit_pos(self):
        """The bit position getter.

        Returns:
            An integer. (from 0 to len(data) - 1)

        """

        return self.byte_ptr * 8 + self.bit_ptr

    @bit_pos.setter
    def bit_pos(self, bits):
        """The bit position setter.

        Args:
            bits: The number of bits to set from the beginning of data.

        """

        if bits > len(self):
            raise BitReaderError('bit_pos(%s) is out of boundary', bits)

        self.byte_ptr, self.bit_ptr = divmod(bits, 8)

    def __len__(self):
        """Return the data size in bits.

        Returns:
            An integer.

        """

        return len(self.data) * 8

    def read(self, bit_length):
        """Read bit_length bits as an integer.

        Args:
            bit_length: An integer indicating how many bits to read.

        Returns:
            An integer value.

        """

        ret = self.peek(bit_length)
        self.bit_pos += bit_length
        return ret

    def peek(self, bit_length):
        """Read bit_length as an integer without advancing pointer.

        Args:
            bit_length: An integer indicating how many bits to read.

        Returns:
            An integer.

        """

        if bit_length < 0:
            raise BitReaderError('bit_length(%s) should be greater than 0',
                                 bit_length)
        elif self.bit_pos + bit_length > len(self):
            raise BitReaderError('out of data boundary')

        ret = 0
        byte_ptr, bit_ptr = self.byte_ptr, self.bit_ptr

        while bit_length > 0:
            byte = ord(self.data[byte_ptr])
            remaining_bits = 8 - bit_ptr

            if bit_length > remaining_bits:
                bit_length -= remaining_bits
                ret |= ((byte & ((1 << remaining_bits) - 1)) << bit_length)
                byte_ptr += 1
                bit_ptr = 0
            else:
                ret |= ((byte >> (remaining_bits - bit_length)) & \
                        ((1 << bit_length) - 1))
                break

        return ret

