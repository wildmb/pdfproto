#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports


class RunLengthDecoder:

	def decode(self, data):

		ret = []
		i = 0
		data_len = len(data)

		while i < data_len:

			length = ord(data[i])

			if length == 128:
				break

			if 0 <= length < 128:
				ret.append(data[(i + 1):(i + 1 + length + 1)])
				i = (i + 1) + (length + 1)

			if length > 128:
				ret.append(data[i + 1] * (257 - length))
				i = (i + 1) + 1

		return ''.join(ret)
