'''Implements basic interface of UUID and uuid4()
'''
import os
import ubinascii

# The cpython UUID class takes "int" as argument name 
# but we need to reference real int function below
_from_bytes = int.from_bytes


class UUID:
    def __init__(self, hex=None, bytes=None, bytes_le=None, fields=None, int=None):
        if hex:
            b = ubinascii.unhexlify(hex.strip('{}').replace('-', ''))
            if len(b) != 16:
                raise ValueError('string args must be in long uuid format')
            self._int = _from_bytes(b, 'big')

        elif bytes:
            if len(bytes) != 16:
                raise ValueError('bytes must be 16 bytes')
            self._int = _from_bytes(bytes, 'big')

        elif bytes_le:
            if len(bytes_le) != 16:
                raise ValueError('bytes_le must be 16 bytes')
            self._int = _from_bytes(bytes_le[:4], 'little') << 96
            self._int |= _from_bytes(bytes_le[4:6], 'little') << 80
            self._int |= _from_bytes(bytes_le[6:8], 'little') << 64
            self._int |= _from_bytes(bytes_le[8:], 'big')


        elif fields:
            if len(fields) != 6:
                raise ValueError('fields must be the six integer fields of the UUID')
            self._int = fields[0]<<96
            self._int |= fields[1]<<80
            self._int |= fields[2]<<64
            self._int |= fields[3]<<56
            self._int |= fields[4]<<48
            self._int |= fields[5]<<0

        elif int:
            self._int = int

        else:
            raise ValueError("No valid argument passed")

    @property
    def hex(self):
        return '%032x' % self._int
            
    def __str__(self):
        hex = '%032x' % self._int
        return '%s-%s-%s-%s-%s' % (
               hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

    def __repr__(self):
        return "<UUID: {%s}>" % str(self)

    def __bytes__(self):
        return self._int.to_bytes(16, 'big')

    def __int__(self):
        return self._int

    def __hash__(self):
        return hash(self._int)

    def __eq__(self, other):
        if isinstance(other, UUID):
            return other.__int__() == self._int


def uuid4():
    '''Generates a random UUID compliant to RFC 4122 pg.14 '''
    random = bytearray(os.urandom(16))
    random[6] = (random[6] & 0x0F) | 0x40
    random[8] = (random[8] & 0x3F) | 0x80
    return UUID(bytes=random)
