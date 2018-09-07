# (c) 2018 Paul Sokolovsky. MIT license.
from ucollections import OrderedDict
import uctypes
from uctypes import (
    UINT8, INT8, UINT16, INT16, UINT32, INT32
)

def STRUCT(typ):
    return (0, typ)

def PTR(typ):
    return (uctypes.PTR, typ)

def ARRAY(typ, sz):
    if isinstance(typ, int):
        return (uctypes.ARRAY, typ | sz)
    return (uctypes.ARRAY, sz, typ)

def UNION(fields):
    res = OrderedDict()
    off = 0
    for k, t in fields.items():
        if isinstance(t, tuple):
            assert t[0] == 0
            res[k] = (off, t[1])
        else:
            res[k] = off | t
        off = uctypes.PREV_OFFSET
    return res

def BITFIELD(pos, len, type=UINT32):
    return (type + (uctypes.BFUINT8 - uctypes.UINT8)) | pos << uctypes.BF_POS | len << uctypes.BF_LEN

bitfield_type = None
bitfield_pos = None

def C_BITFIELD_1ST(len, type=UINT32):
    global bitfield_type, bitfield_pos
    bitfield_type = type + (uctypes.BFUINT8 - uctypes.UINT8)
    bitfield_pos = len
    return bitfield_type | 0 << uctypes.BF_POS | len << uctypes.BF_LEN

def C_BITFIELD_NEXT(len):
    global bitfield_type, bitfield_pos
    ret = bitfield_type | bitfield_pos << uctypes.BF_POS | len << uctypes.BF_LEN
    bitfield_pos += len
    return ret
