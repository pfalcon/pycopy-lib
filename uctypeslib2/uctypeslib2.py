# (c) 2018 Paul Sokolovsky. MIT license.
from micropython import const


VAL_TYPE_BITS = const(4)
BITF_LEN_BITS = const(5)
BITF_OFF_BITS = const(5)
OFFSET_BITS = const(17)
AGG_TYPE_BITS = const(2)

assert VAL_TYPE_BITS + BITF_LEN_BITS + BITF_OFF_BITS + OFFSET_BITS == 31

OFFSET_MASK = (1 << OFFSET_BITS) - 1
TYPES = (
    "UINT8", "INT8", "UINT16", "INT16",
    "UINT32", "INT32", "UINT64", "INT64",

    "BFUINT8", "BFINT8", "BFUINT16", "BFINT16",
    "BFUINT32", "BFINT32",

    "FLOAT32", "FLOAT64",
)
AGG_TYPES = ("STRUCT", "PTR", "ARRAY")


def pprint(desc, stream=None, cur_ind=0):

    def valtype(v):
        return (v & 0x7fff_ffff) >> (31 - VAL_TYPE_BITS)

    print("{", file=stream)

    for k, v in desc.items():
        print("  " * cur_ind, end="", file=stream)
        if isinstance(v, tuple):
            t = (v[0] & 0x7fff_ffff) >> (31 - AGG_TYPE_BITS)
            off = v[0] & OFFSET_MASK
            if t == 0:
                print("%r: (%d, "% (k, v[0]), end="", file=stream)
                pprint(v[1], stream, cur_ind + 1)
                print("),", file=stream)
            elif t == 1:
                print("%r: (%d | %s, %s)," % (k, off, AGG_TYPES[t], TYPES[valtype(v[1])]),
                      file=stream)
            elif t == 2:
                if len(v) == 2:
                    print("%r: (%d | %s, %s | %d)," % (
                            k, off, AGG_TYPES[t], TYPES[valtype(v[1])], v[1] & OFFSET_MASK),
                        file=stream)
                else:
                    print("%r: (%d | %s, %d, " % (k, off, AGG_TYPES[t], v[1]), end="", file=stream)
                    pprint(v[2], stream, cur_ind + 1)
                    print("),", file=stream)
            else:
                assert False, "unimpl: %t" % t
        else:
            t = valtype(v)
            if 8 <= t < 14:
                pos = (v >> uctypes.BF_POS) & 0x1f
                sz = (v >> uctypes.BF_LEN) & 0x1f
                print("%r: %d | %s | %d << uctypes.BF_POS | %d << uctypes.BF_LEN," % (k, v & OFFSET_MASK, TYPES[t], pos, sz))
            else:
                print("%r: %d | %s," % (k, v & OFFSET_MASK, TYPES[t]))

    end = "\n" if cur_ind == 0 else ""
    print("}", end=end, file=stream)
