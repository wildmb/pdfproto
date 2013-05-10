#!/usr/bin/env python

# standard library imports
from contextlib import closing
import mmap
import re

# third party related imports

# local library imports


class SimplePDFScanner(object):

    RE_OBJ_PATTERN = re.compile(r'(\d+) (\d+) obj[\r|\n|\r\n]')

    def __init__(self, filename):

        self.filename = filename
        self.object_list = []
        self._scan()

    def _scan(self):

        with closing(open(self.filename, 'rb')) as f:
            with closing(mmap.mmap(f.fileno(), 0,
                                   prot=mmap.PROT_READ)) as stream:
                for match_obj in self.RE_OBJ_PATTERN.finditer(stream):
                    obj_num, gen_num = match_obj.groups()
                    offset = match_obj.start()
                    obj = (int(obj_num), int(gen_num), offset)
                    self.object_list.append(obj)

    @property
    def objects(self):
        return self.object_list


if __name__ == "__main__":

    import sys, json

    if len(sys.argv) != 2:
        print 'usage: python %s pdf' % (sys.argv[0])
        exit(1)

    scanner = SimplePDFScanner(sys.argv[1])
    print json.dumps(scanner.objects, indent=4)
