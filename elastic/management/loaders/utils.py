import sys
import re


class GFF:
    ''' GFF file object - based on GFF3 specifications '''

    def __init__(self, line='dummy\tdummy\tregion\t' + str(sys.maxsize) +
                 '\t-1\t.\t.\t.\t\t', field_delim=';', key_value_delim='='):
        parts = re.split('\t', line)
        if(len(parts) != 9):
            raise GFFError("GFF error: wrong number of columns")
        self.seqid = parts[0]
        self.source = parts[1]
        self.type = parts[2]
        self.start = int(parts[3])
        self.end = int(parts[4])
        self.score = parts[5]
        self.strand = parts[6]
        self.phase = parts[7]
        self.attrStr = parts[8]
        self.attrs = {}
        self._parseAttributes(field_delim, key_value_delim)

    def _parseAttributes(self, field_delim, key_value_delim):
        ''' Parse the attributes column '''
        parts = re.split(field_delim, self.attrStr.strip())
        for p in parts:
            if(p == ''):
                continue
            at = re.split(key_value_delim, p.strip())
            if len(at) == 2:
                self.attrs[at[0]] = at[1]
            else:
                self.attrs[at[0]] = ""

    def getAttributes(self):
        return self.attrs


class GFFError(Exception):
    ''' GFF parse error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
