from stats.DPDuration import DPDuration, DPTypeDuration
from stats.Symbol import Symbol
from stats.Data import Addr, AddrRange


class Stats:
    """
    A statistics object with a collection of data points.
    """

    def __init__(self):
        # The duration data points for a given library.
        self.duration_dps: dict[DPTypeDuration, DPDuration] = dict()
        self.max_ram: int = 0
        self.symbols: dict[str, Symbol] = dict()

    def add_dps_duration(self, dps: dict[DPTypeDuration, DPDuration]):
        self.duration_dps.update(dps)

    def add_max_ram(self, max_ram: int):
        self.max_ram = max_ram

    def add_symbols(self, symbols: dict[str, Symbol]):
        self.symbols.update(symbols)

    def get_max_ram_mb(self) -> str:
        return f"{self.max_ram / 1000000:.2f} MB"

    def get_runtime_ms(self, type: DPTypeDuration) -> float | None:
        if type not in self.duration_dps:
            return None
        return self.duration_dps[type].get_delta_ms()

    def tanimoto_similarity_symbol(a: Symbol, b: Symbol) -> float:
        """
        Measures the Tanimoto difference between two functions.
        Tanimoto similarity is apparently the same as Jaccard index,
        but I found the Tanimoto similarity easier to get,
        because it is defined for bit vectors.
        Math which just works out of the box, you know.

        The similarity is calculated by:
        T(X,Y) = SUM_i(X[i] & Y[i]) / SUM_i(X[i] | Y[i])

        Here the bit vectors are the Symbols' address ranges:
        X[i] is 1 iff byte i is covered by one of the ranges.
        Bytes covered are a set of disjoint intervals, so instead of
        iterating bit by bit we merge overlapping ranges and sweep the
        interval boundaries: the number of set intersection bits is the
        sum of the intersection lengths, and likewise for the union.

        https://en.wikipedia.org/wiki/Jaccard_index#Tanimoto_similarity_and_distance
        """
        a_ranges = Stats._merged_ranges(a)
        b_ranges = Stats._merged_ranges(b)

        intersection = 0
        i = j = 0
        while i < len(a_ranges) and j < len(b_ranges):
            lo = max(a_ranges[i][0], b_ranges[j][0])
            hi = min(a_ranges[i][1], b_ranges[j][1])
            if lo < hi:
                intersection += hi - lo
            if a_ranges[i][1] < b_ranges[j][1]:
                i += 1
            else:
                j += 1

        union = (
            sum(hi - lo for lo, hi in a_ranges)
            + sum(hi - lo for lo, hi in b_ranges)
            - intersection
        )
        if union == 0:
            return 0.0
        return intersection / union

    @staticmethod
    def _merged_ranges(symbol: Symbol) -> list[AddrRange]:
        """
        Returns the symbol's address ranges as a sorted list of
        disjoint right-open intervals, with overlapping ranges merged.
        """
        merged: list[list[Addr]] = list()
        for lo, hi in sorted(
            (lo, hi) for lo, hi in symbol.ranges if hi > lo
        ):
            if merged and lo <= merged[-1][1]:
                if hi > merged[-1][1]:
                    merged[-1][1] = hi
            else:
                merged.append([lo, hi])
        return merged
