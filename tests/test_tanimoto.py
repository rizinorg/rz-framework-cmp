from stats.Symbol import Symbol, SymbolType
from stats.Stats import Stats
from stats.Data import Addr

import pytest


def test_100_match_I():
    a = Symbol("a", SymbolType.FUNCTION, 0, 0x5000)
    b = Symbol("b", SymbolType.FUNCTION, 0, 0x5000)
    a.add_range((Addr(0x5000), Addr(0x5010)))
    b.add_range((Addr(0x5000), Addr(0x5010)))
    assert Stats.tanimoto_similarity_symbol(a, b) == 1


def test_100_match_II():
    a = Symbol("a", SymbolType.FUNCTION, 0, 0x5000)
    b = Symbol("b", SymbolType.FUNCTION, 0, 0x5000)
    a.add_range((Addr(0x5000), Addr(0x5010)))
    b.add_range((Addr(0x5000), Addr(0x5010)))
    a.add_range((Addr(0x5040), Addr(0x5052)))
    b.add_range((Addr(0x5040), Addr(0x5052)))
    a.add_range((Addr(0x5060), Addr(0x5060)))
    b.add_range((Addr(0x5060), Addr(0x5060)))
    assert Stats.tanimoto_similarity_symbol(a, b) == 1


def test_partly_match_I():
    a = Symbol("a", SymbolType.FUNCTION, 0, 0x5000)
    b = Symbol("b", SymbolType.FUNCTION, 0, 0x5000)
    a.add_range((Addr(0x5001), Addr(0x5009)))
    b.add_range((Addr(0x5000), Addr(0x5010)))
    assert Stats.tanimoto_similarity_symbol(a, b) == (0x8 / 0x10)


def test_partly_match_II():
    a = Symbol("a", SymbolType.FUNCTION, 0, 0x5000)
    b = Symbol("b", SymbolType.FUNCTION, 0, 0x5000)
    a.add_range((Addr(0x5001), Addr(0x5009)))
    b.add_range((Addr(0x5000), Addr(0x5010)))
    a.add_range((Addr(0x6000), Addr(0x6010)))
    b.add_range((Addr(0x7000), Addr(0x7010)))
    assert Stats.tanimoto_similarity_symbol(a, b) == (0x8 / 0x30)


def test_partly_match_III():
    a = Symbol("a", SymbolType.FUNCTION, 0, 0x5000)
    b = Symbol("b", SymbolType.FUNCTION, 0, 0x5000)
    a.add_range((Addr(0x1001), Addr(0x1009)))
    b.add_range((Addr(0x5000), Addr(0x5010)))
    a.add_range((Addr(0x6000), Addr(0x6010)))
    b.add_range((Addr(0x7000), Addr(0x7010)))
    assert Stats.tanimoto_similarity_symbol(a, b) == 0.0
