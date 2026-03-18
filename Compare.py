#!/usr/bin/env python3
import multiprocessing

from prettytable import PrettyTable
from pathlib import Path
import argparse
import logging as log

from multiprocessing.pool import ThreadPool
import time
import psutil
import os

from Binary import Binary, init_binary
from Framework import (
    FRAMEWORK_NAMES,
    FRAMEWORK_RIZIN,
    FRAMEWORK_RIZIN_OLD_ANALYSIS,
    Framework,
    init_framework_by_name,
)
from stats.Stats import Stats
from stats.DPDuration import DPTypeDuration


class Comparator:
    MAX_BINARIES = 10

    def __init__(self, bin_path: Path, framework_names: list[str]):
        # Statistics for each (Framework, Binary) combination
        self.stats: dict[tuple[Framework, Binary], Stats] = dict()
        self.bins: list[Binary] = list()
        self.framework_names: list[str] = framework_names
        self.frameworks: dict[str, Framework] = dict()
        self.load_binaries(bin_path)
        self.init_frameworks()

    def load_binaries(self, bin_path: Path):
        i = 0
        for bp in list(bin_path.glob("**/*")) + [bin_path]:
            if bp.is_dir():
                continue
            if not bp.exists():
                log.warning(f"File '{bp}' doesn't exist.")
                continue

            try:
                bin = init_binary(bp)
                log.info(f"Add '{bp}' with {len(bin.symbols)} symbols")
                self.bins.append(bin)
                i += 1
            except Exception as e:
                log.error(f"Load error for '{bp}'.")
                # log.error(repr(e))
                raise e

            if i > self.MAX_BINARIES:
                log.warning(f"Added maxiumum of {self.MAX_BINARIES} files. Stop.")
                break
        log.info(f"Added {len(self.bins)} binaries")

    def init_frameworks(self):
        for fname in self.framework_names:
            self.frameworks[fname] = init_framework_by_name(fname)
            log.info(f"Initialized {fname}")

    def analyze_all(self):
        process = psutil.Process(os.getpid())
        for fw_name, fw in self.frameworks.items():
            for bin in self.bins:
                log.info(f"Analyzing '{bin.path.name}' with {fw_name}")
                stop_event = multiprocessing.Event()

                def track_max_mem():
                    max_mem = 0
                    while not stop_event.is_set():
                        mem = process.memory_info().rss
                        if mem > max_mem:
                            max_mem = mem
                        time.sleep(0.5)
                    return max_mem

                pool = ThreadPool(processes=2)
                track_ram_usage = pool.apply_async(track_max_mem)

                fw_ana_ret = pool.apply_async(fw.analyze_bin, [bin])

                dps = fw_ana_ret.get()

                # Stop tracking mem
                stop_event.set()
                max_ram = track_ram_usage.get()

                stats = Stats()
                stats.add_dps_duration(dps)
                stats.add_max_ram(max_ram)
                stats.add_symbols(fw.symbols)
                self.stats[(fw, bin)] = stats
                log.info(f"{fw_name} found {len(fw.symbols)} symbols.")

    def symbol_comparison_table(self):
        if len(self.stats) == 0:
            log.error("Analysis must run to collect data.")
            return

        print("Tanimoto Similarity Score\n-------------------------\n")

        # One table per Binary
        for bin in self.bins:
            table = PrettyTable()
            field_names = ["Symbol", "Type", "Bin"] + self.framework_names
            table.field_names = field_names

            scores: dict[str, dict[str, str]] = dict()
            for sym_name in bin.symbols.keys():
                scores[sym_name] = {"bin": "1.0"}

            # Maps symbol names detected by frameworks, but not in the binary info,
            # to the frameworks which discovered them.
            fw_only_symbols: dict[str, list[str]] = dict()

            for fw_name in self.framework_names:
                fw: Framework = self.frameworks[fw_name]
                for sym_name, symbol in fw.symbols.items():
                    if sym_name not in scores.keys():
                        # A symbol detected by the framework, but not present
                        # in the binary info
                        if sym_name not in fw_only_symbols:
                            fw_only_symbols[sym_name] = list()
                        fw_only_symbols[sym_name].append(fw_name)
                    else:
                        t = Stats.tanimoto_similarity_symbol(
                            bin.symbols[sym_name], symbol
                        )
                        scores[sym_name].update({fw_name: f"{t:.2f}"})

            sym_names = list(scores.keys())
            sym_names.sort()

            for sym_name in sym_names:
                table.add_row(
                    [sym_name, bin.symbols[sym_name].type, "1.0"]
                    + [
                        scores[sym_name][fwn] if fwn in scores[sym_name] else "-"
                        for fwn in self.framework_names
                    ]
                )

            fw_only_rows = list()
            for sym_name, fw_names in fw_only_symbols.items():
                fw_only_rows.append(
                    [sym_name, "-", "-"]
                    + ["x" if fwn in fw_names else "-" for fwn in self.framework_names]
                )

            table.add_rows(fw_only_rows)
            table.align = "l"
            print(f"FILE: {bin.path}")
            print(table.get_string(sortby="Symbol"))

    def runtime_comparison_table(self):
        if len(self.stats) == 0:
            log.error("Analysis must run to collect data.")
            return
        print("Runtime measurements\n--------------------\n")
        # One table per Binary
        for bin in self.bins:
            table = PrettyTable()
            field_names = ["Framework", "Open file", "Analysis", "Max RAM"]
            table.field_names = field_names

            for fw_name, fw in self.frameworks.items():
                if (fw, bin) not in self.stats:
                    table.add_row([fw_name, "-", "-"])
                    continue
                stats = self.stats[(fw, bin)]

                rt = stats.get_runtime_ms(DPTypeDuration.RUNTIME_OPEN_FILE)
                if not rt:
                    log.error("Failed to get runtime RUNTIME_OPEN_FILE")
                    rt = 0
                open_rt = rt / 1000
                rt = stats.get_runtime_ms(DPTypeDuration.RUNTIME_ANALYZE_ALL)
                if not rt:
                    log.error("Failed to get runtime RUNTIME_ANALYZE_ALL")
                    rt = 0
                ana_rt = rt / 1000
                table.add_row(
                    [
                        fw_name,
                        f"{open_rt:.2f} s",
                        f"{ana_rt:.2f} s",
                        f"{stats.get_max_ram_mb()}",
                    ]
                )

            print(f"FILE: {bin.path}")
            print(table)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug output"
    )
    parser.add_argument(
        "-f",
        "--frameworks",
        help="The frameworks to compare.",
        nargs="+",
        choices=FRAMEWORK_NAMES,
        default=[FRAMEWORK_RIZIN, FRAMEWORK_RIZIN_OLD_ANALYSIS],
    )
    parser.add_argument(
        "bin_path",
        help="Path to one binary or a directory of binaries (walked recursively) for comparison.",
        type=Path,
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    log.basicConfig(level=log.DEBUG if args.verbose else log.INFO)
    comparator = Comparator(args.bin_path, args.frameworks)
    comparator.analyze_all()
    print("\nRESULTS\n=======\n")
    comparator.runtime_comparison_table()
    print("\n")
    comparator.symbol_comparison_table()
