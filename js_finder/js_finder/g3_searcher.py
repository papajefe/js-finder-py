"""G3 Searcher module for pyodide to access"""

from itertools import chain, product
import sys
from typing import Iterable
import numpy as np
from numba_pokemon_prngs.lcrng import PokeRNGRMod
from numba_pokemon_prngs.data import NATURES_EN


def main():
    """Main function to be run for the g3_searcher module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from g3 searcher!")
    print(f"{sys.version=}")

def recover_from_ivs(method: int, ivs: tuple[int]) -> Iterable[int]:
    """Recover all PRNG states that produce the specified IVs"""
    assert method in (1, 2, 4)
    if method == 4:
        add = 0xE97E7B6A
        mult = 0xC2A29A69
        mod = 0x3A89
        pat = 0x2E4C
        inc = 0x5831
    else:
        add = 0x6073
        mult = 0x41C64E6D
        mod = 0x67D3
        pat = 0xD3E
        inc = 0x4034

    first = (ivs[0] | (ivs[1] << 5) | (ivs[2] << 10)) << 16
    second = (ivs[5] | (ivs[3] << 5) | (ivs[4] << 10)) << 16
    diff = ((second - first * mult) & 0xFFFFFFFF) >> 16
    start_1 = ((((diff * mod + inc) & 0xFFFFFFFF) >> 16) * pat) % mod
    start_2 = (((((diff ^ 0x8000) * mod + inc) & 0xFFFFFFFF) >> 16) * pat) % mod

    for low in chain(range(start_1, 0x10000, mod), range(start_2, 0x10000, mod)):
        seed = first | low
        if ((seed * mult + add) & 0x7FFF0000) == second:
            yield seed
            yield seed ^ 0x80000000

def search(method: int, min_ivs: tuple[int], max_ivs: tuple[int]) -> str:
    """Search for RNG states producing the filtered values"""
    rows = ""
    count = 0
    for ivs in product(
        *(range(minimum, maximum + 1) for minimum, maximum in zip(min_ivs, max_ivs))
    ):
        for seed in recover_from_ivs(method, ivs):
            go = PokeRNGRMod(seed)
            go.next()
            pid = (go.next_u16() << np.uint32(16))
            if method == 2:
                go.next()
            pid |= go.next_u16()
            shiny = False
            nature = pid % 25
            ability = pid & 1

            rows += (
                "<tr>"
                f"<td>{seed:08X}</td>"
                f"<td>{pid:08X}</td>"
                f"<td>{"Yes" if shiny else "No"}</td>"
                f"<td>{NATURES_EN[nature]}</td>"
                f"<td>{ability}</td>"
                f"<td>{"/".join(map(str, ivs))}</td>"
                "</tr>"
            )
            count += 1
            # stop at 1000 results to avoid overworking
            if count >= 1000:
                return rows + "<tr><td>Results Truncated</td></tr>"

    return rows
