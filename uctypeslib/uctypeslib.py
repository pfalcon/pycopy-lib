# (c) 2018 Paul Sokolovsky. MIT license.
from ucollections import OrderedDict
import uctypes
from uctypes import (
    UINT8, INT8, UINT16, INT16, UINT32, INT32,
    UINT64, INT64, FLOAT32, FLOAT64,
    USHORT, SHORT, UINT, INT, ULONG, LONG,
    ULONGLONG, LONGLONG
)

def STRUCT(typ):
    return (0, typ)

def PTR(typ):
    return (uctypes.PTR, typ)

def ARRAY(typ, sz):
    if isinstance(typ, int):
        return (uctypes.ARRAY, typ | sz)
    # Unconvert struct
    if typ[0] == 0:
        return (uctypes.ARRAY, sz, typ[1])
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


__bitfield_type = None
__bitfield_pos = None


# Initial bitfield in set should specify integer type of the field holding
# this set (UINT8, UNIT16, etc.). Following bitfields should omit "type" param.
# lsb is a bit position of least significant bit of the bitfield. The least
# bit of a word has position 0. E.g. in UINT16, least significant 8 bits have
# position 0, most significant - 8.
def BITFIELD(lsb, len, type=None):
    global __bitfield_type
    if type is None:
        off = uctypes.PREV_OFFSET
        type = __bitfield_type
    else:
        off = 0
        __bitfield_type = type
    return off | (type + (uctypes.BFUINT8 - uctypes.UINT8)) | lsb << uctypes.BF_POS | len << uctypes.BF_LEN


# Similar to BITFIELD, but bitfield position is implicit, and is assigned
# per C language rules (starting from position 0 for little-endian architectures;
# TODO: support big-endian way, where positions are assigned from most significant
# bits of a word).
def C_BITFIELD(len, type=None):
    global __bitfield_type, __bitfield_pos
    if type is None:
        off = uctypes.PREV_OFFSET
        type = __bitfield_type
    else:
        off = 0
        __bitfield_type = type
        __bitfield_pos = 0
    ret = off | (type + (uctypes.BFUINT8 - uctypes.UINT8)) | __bitfield_pos << uctypes.BF_POS | len << uctypes.BF_LEN
    __bitfield_pos += len
    return ret
