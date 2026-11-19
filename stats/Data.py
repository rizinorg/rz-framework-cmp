from typing import TypeAlias

# Addresses are plain ints: Python ints are arbitrary precision and thus
# cover the full unsigned 64-bit address range exactly.
Addr: TypeAlias = int

# Tuple of address depicting a range between low and high address.
# Each range is an right open interval: [low, high)
AddrRange: TypeAlias = tuple[Addr, Addr]
