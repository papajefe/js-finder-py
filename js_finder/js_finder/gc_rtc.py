"""GameCube RTC module for pyodide to access"""

import sys
import datetime
from typing import Collection, Iterable
import numpy as np

def modpow32(a_val, b_val):
    """(uint)(a_val ** b_val)"""
    return pow(a_val, b_val, 0x100000000)

# TODO: precomputed jump table
def lcrng_jump(seed, advances, mult, add):
    """Efficiently jump ahead in the LCRNG sequence"""
    advances_left = advances - 1
    mult_val = mult
    add_val = 1
    add_remainder = 0

    while advances_left > 0:
        if (advances_left & 1) == 0:
            add_remainder += add_val * modpow32(mult_val, advances_left)
            advances_left -= 1
        add_val *= (1 + mult_val)
        mult_val *= mult_val
        advances_left >>= 1

        add_val &= 0xFFFFFFFF
        add_remainder &= 0xFFFFFFFF
        mult_val &= 0xFFFFFFFF

    final_mult = modpow32(mult, advances)
    final_add = ((add_val + add_remainder) * add) & 0xFFFFFFFF
    return (seed * final_mult + final_add) & 0xFFFFFFFF

def distance(state0, state1):
    """Efficiently calculate the distance between two gamecube initial seeds from outdated dolphin"""
    # the lower 5 bits are never modified by tha addition caused by seconds passing
    # if this is not already equal it will never be
    if state0 & 0x1F != state1 & 0x1F:
        return None
    state0 >>= 5
    state1 >>= 5
    mask = 1
    dist = 0

    while state0 != state1:
        if (state0 ^ state1) & mask:
            state0 = (state0 + (1265625 * mask)) & 0x7FFFFFF
            dist += mask
        mask <<= 1

    return dist

def gc_rtc(
    origin_seed: int, target_seed: int, min_advances: int, num_results: int
) -> Iterable[Collection[int]]:
    """Find initial seed results"""
    i = 0
    advance = min_advances
    target_seed = lcrng_jump(target_seed, advance, 0xB9B33155, 0xA170F641)
    while i < num_results:
        dist = distance(origin_seed, target_seed)
        if dist is not None:
            yield (target_seed, advance, dist)
            i += 1
        target_seed = (target_seed * 0xB9B33155 + 0xA170F641) & 0xFFFFFFFF
        advance += 1

def main():
    """Main function to be run for the gc_rtc module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from GC RTC!")
    print(f"{sys.version=}")


def run_gc_rtc(origin_seed: int, target_seed: int, min_advances: int, num_results: int) -> str:
    """Run GC RTC to find initial seeds"""

    return "".join(
        (
            "<tr>"
            f"<td>{seed:08x}</td>"
            f"<td>{advance}</td>"
            f"<td>{datetime.datetime(year=2000, month=1, day=1) + datetime.timedelta(seconds=timestamp)}</td>"
            "</tr>"
        )
        for (seed, advance, timestamp) in gc_rtc(
            origin_seed, target_seed, min_advances, num_results
        )
    )
