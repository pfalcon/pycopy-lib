from ucollections import OrderedDict as od
import uctypes
import uctypeslib as uc

desc = od((
    ("s0", uc.UINT16),
    ("sub", uc.STRUCT(od((
        ("b0", uc.UINT8),
        ("b1", uc.UINT8),
    )))),
    ("arr", uc.ARRAY(uctypes.UINT8, 2)),
    ("arr2", uc.ARRAY({"b": uctypes.UINT8}, 2)),

    ("bitf0", uc.BITFIELD(0, 8, type=uc.UINT16)),
    ("bitf1", uc.BITFIELD(8, 8)),

    ("bf0", uc.C_BITFIELD(4, type=uc.UINT16)),
    ("bf1", uc.C_BITFIELD(4)),
    ("bf2", uc.C_BITFIELD(4)),
    ("bf3", uc.C_BITFIELD(4)),
))

sizeof = uctypes.calc_offsets(desc, uctypes.LITTLE_ENDIAN)

data = bytearray(sizeof)

S = uctypes.struct(uctypes.addressof(data), desc, uctypes.LITTLE_ENDIAN)

S.s0 = 0x0102
S.sub.b0 = 3
S.sub.b1 = 4
S.arr[0] = 5
S.arr[1] = 6
S.arr2[0].b = 7
S.arr2[1].b = 8

S.bitf0 = 9
S.bitf1 = 0xa

S.bf0 = 0xb
S.bf1 = 0xc
S.bf2 = 0xd
S.bf3 = 0xe

print(data)

assert data == b"\x02\x01\x03\x04\x05\x06\x07\x08\t\n\xcb\xed"
