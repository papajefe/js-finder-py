"""G3 Searcher module for pyodide to access"""

from .util import frame_to_ms
import sys
from typing import Iterable
import numpy as np
from numba_pokemon_prngs.lcrng import PokeRNGMod
from numba_pokemon_prngs.data import NATURES_EN
from .ten_lines import FRLG_DATA


def main():
    """Main function to be run for the g3_calibration module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from g3 calibration!")
    print(f"{sys.version=}")

def check_frlg(
    method: int,
    tsv: int,
    min_ivs: tuple[int],
    max_ivs: tuple[int],
    base_seed: int,
    leeway: int,
    game: str,
    sound: str,
    l: str,
    button: str,
    select: str,
    advance_min: int,
    advance_max: int,
):
    seed_data = FRLG_DATA[game][sound][l][button][select]
    datum = seed_data.get(str(base_seed), None)
    if datum is None:
        return "<td>Invalid Target Seed</td>"
    idx = datum[1]
    return check_iter(
        method,
        tsv,
        min_ivs,
        max_ivs,
        tuple(seed_data.items())[max(idx-leeway, 0):idx+leeway+1],
        advance_min,
        advance_max,
    )


def check_iter(
    method: int,
    tsv: int,
    min_ivs: tuple[int],
    max_ivs: tuple[int],
    seed_data: Iterable[tuple[int, tuple[int, int]]],
    advance_min: int,
    advance_max: int,
) -> str:
    """Search for RNG states producing the filtered values in the provided seed and advance ranges"""
    rows = ""
    count = 0
    for initial_seed, (seed_frame, _idx) in seed_data:
        initial_seed = int(initial_seed)
        rng = PokeRNGMod(initial_seed)
        rng.advance(advance_min)
        for advance in range(advance_min, advance_max + 1):
            go = PokeRNGMod(rng.seed)
            rng.next()
            low = go.next_u16()
            high = go.next_u16()
            pid = low | (high << np.uint32(16))
            if method == 2:
                go.next()
            shiny_value = tsv ^ low ^ high
            # if shiny_value >= shiny_filter:
            #     continue
            nature = pid % 25
            ability = pid & 1
            iv0 = go.next_u16()
            if method == 4:
                go.next()
            iv1 = go.next_u16()
            ivs = (
                iv0 & 31,
                (iv0 >> 5) & 31,
                (iv0 >> 10) & 31,
                (iv1 >> 5) & 31,
                (iv1 >> 10) & 31,
                iv1 & 31,
            )
            if not all(min_iv <= iv <= max_iv for iv, min_iv, max_iv in zip(ivs, min_ivs, max_ivs)):
                continue

            rows += (
                "<tr>"
                f"<td>{initial_seed:04X} | {frame_to_ms(seed_frame)}ms</td>"
                f"<td>{advance}</td>"
                f"<td>{pid:08X}</td>"
                f"<td>{"Square" if shiny_value == 0 else "Star" if shiny_value < 8 else "No"}</td>"
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
