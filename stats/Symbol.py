from stats.Data import Addr, AddrRange

from enum import Enum


class SymbolType(Enum):
    UNSPECIFIED = 0
    FUNCTION = 1
    OBJECT = 2

    def __str__(self):
        return f"{self.name}"


class Symbol:
    def __init__(self, name: str, type: SymbolType, size: int, location: Addr):
        self.name = name
        self.type = type
        self.size = size
        self.location = location
        self.ranges: list[AddrRange] = list()
        match type:
            case SymbolType.OBJECT:
                self.add_range((location, location + Addr(size)))
            case _:
                pass

        self.entry_points: list[Addr] = list()

    def add_range(self, range: AddrRange):
        self.ranges.append(range)

    def add_entry_point(self, entry_point: Addr):
        self.entry_points.append(entry_point)

    def get_n_bytes(self) -> int:
        """
        Returns total number of bytes this symbol covers.
        It will always use Symbol.ranges for this calculation.
        """
        return sum([r[1] - r[0] for r in self.ranges]).is_integer()

    def __repr__(self):
        return f"SYMBOL<{self.name} | type: {self.type} | entries: {[e for e in self.entry_points]} | ranges: {[e for e in self.ranges]}>"
