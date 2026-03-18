from stats.DPDuration import DPDuration, DPTypeDuration
from stats.Symbol import Symbol
from stats.Data import Addr


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

        In the calculation here we compare the address ranges.
        So effectively check how many bytes in the Symbols' address ranges overlap.

        https://en.wikipedia.org/wiki/Jaccard_index#Tanimoto_similarity_and_distance
        """
        covered = [x for x in sorted(a.ranges + b.ranges, key=lambda r: r[0])]
        sum_dividend = 0
        sum_divisor = 0
        i: Addr = Addr(0)
        for r in covered:
            if i > r[1]:
                continue
            if i not in range(r[0], r[1]):
                i = r[0]
            while i < r[1]:
                A_i = any([i in range(r[0], r[1]) for r in a.ranges])
                B_i = any([i in range(r[0], r[1]) for r in b.ranges])

                sum_dividend += 1 if A_i and B_i else 0
                sum_divisor += 1 if A_i or B_i else 0
                i += Addr(1)
        if sum_divisor == 0:
            return 0.0
        return sum_dividend / sum_divisor
