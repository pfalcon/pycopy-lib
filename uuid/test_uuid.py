import uuid

u1 = uuid.uuid4()
u2 = uuid.uuid4()

assert str(u1) != str(u2), "Two uuid4 should not match"

same = {
    uuid.UUID('{12345678-1234-5678-1234-567812345678}'),
    uuid.UUID('12345678123456781234567812345678'),
    uuid.UUID('12345678-1234-5678-1234-567812345678'),
    uuid.UUID(bytes=b'\x12\x34\x56\x78'*4),
    uuid.UUID(bytes_le=b'\x78\x56\x34\x12\x34\x12\x78\x56' +
                  b'\x12\x34\x56\x78\x12\x34\x56\x78'),
    uuid.UUID(fields=(0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x567812345678)),
    uuid.UUID(int=0x12345678123456781234567812345678)
}

print(same)

assert len(same) == 1, "Alternate methods of initialising UUID should match"

u3 = same.pop()

assert str(u3) == '12345678-1234-5678-1234-567812345678', "str convertion should create standard uuid representation"

assert u3.hex == '12345678123456781234567812345678'

assert u3.__bytes__() == b'\x12\x34\x56\x78'*4

print("OK")
