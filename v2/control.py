import struct


class BytableObject:
    def __init__(self, value, format):
        self.value = value
        self.format = format

    def get_size(self):
        return struct.calcsize(self.format)


class ControlState:
    def __init__(self):
        self._horizontal = BytableObject(0.0, "f")
        self._vertical = BytableObject(0.0, "f")
        self._select = BytableObject(False, "?")
        self._a = BytableObject(False, "?")
        self._b = BytableObject(False, "?")

    @property
    def horizontal(self):
        return self._horizontal

    @property
    def vertical(self):
        return self._vertical

    @property
    def select(self):
        return self._select

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    def to_bytes(self):
        members = [getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and attr.startswith("_")]

        size = 0

        for member in members:
            size = size + member.get_size()

        res = bytearray(size)
        offset = 0

        for member in members:
            struct.pack_into(member.format, res, offset, member.value)
            offset = offset + member.get_size()

        return res

    def from_bytes(self, buffer):
        members = [getattr(self, attr) for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__") and attr.startswith("_")]

        offset = 0

        for member in members:
            member.value = struct.unpack_from(member.format, buffer, offset)[0]
            offset = offset + member.get_size()