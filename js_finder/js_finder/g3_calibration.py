"""G3 Searcher module for pyodide to access"""

from .util import frame_to_ms
import sys
from typing import Iterable
import numpy as np
from numba_pokemon_prngs.lcrng import PokeRNGMod
from numba_pokemon_prngs.data import NATURES_EN, SPECIES_EN
from numba_pokemon_prngs.data.personal import PERSONAL_INFO_FR
from .ten_lines import FRLG_DATA


def main():
    """Main function to be run for the g3_calibration module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from g3 calibration!")
    print(f"{sys.version=}")


def fetch_species_options():
    return "".join(f'<option value="{i}">{species}</option>' for i,species in enumerate(SPECIES_EN[1:387], 1))

def try_intersect(x, y):
    try:
        return range(max(x[0], y[0]), min(x[-1], y[-1]) + 1)
    except IndexError:
        return range(32, 0)

def calc_stat(stat_index, base_stat, iv, level, nature):
    iv_map = (-1, 0, 1, 3, 4, 2)
    stat = np.uint16(
        np.uint16((np.uint16(2) * base_stat + iv) * level) // np.uint16(100)
    )
    nature_boost = nature // np.uint8(5)
    nature_decrease = nature % np.uint8(5)
    if stat_index == 0:
        stat += np.uint16(level) + np.uint16(10)
    else:
        stat += np.uint16(5)
        if nature_boost != nature_decrease:
            if iv_map[stat_index] == nature_boost:
                stat = np.uint16(stat * np.float32(1.1))
            elif iv_map[stat_index] == nature_decrease:
                stat = np.uint16(stat * np.float32(0.9))
    return stat

def calc_ivs(base_stats, stats, level, nature):
    min_ivs = np.ones(6, np.uint16) * 31
    max_ivs = np.zeros(6, np.uint16)
    for i in range(6):
        for iv in range(32):
            stat = calc_stat(i, base_stats[i], np.uint8(iv), np.uint8(level), np.uint8(nature))
            if stat == stats[i]:
                min_ivs[i] = min(iv, min_ivs[i])
                max_ivs[i] = max(iv, max_ivs[i])
    return tuple(
        range(min_iv, max_iv + 1) for min_iv, max_iv in zip(min_ivs, max_ivs)
    )

def calculate_ivs(species: int, nature: int, stat_entry: str):
    personal_info = PERSONAL_INFO_FR[species]
    base_stats = np.array(
        (
            personal_info.hp,
            personal_info.attack,
            personal_info.defense,
            personal_info.special_attack,
            personal_info.special_defense,
            personal_info.speed,
        ),
        np.uint16,
    )
    iv_ranges = [range(32) for _ in range(6)]
    for line in stat_entry.split("\n"):
        level, hp, atk, def_, spa, spd, spe = map(int, line.split())
        stats = np.array((hp, atk, def_, spa, spd, spe), np.uint16)
        iv_ranges = [
            try_intersect(x, y)
            for x, y in zip(
                iv_ranges,
                calc_ivs(
                    base_stats, stats, level, np.int8(nature)
                ),
            )
        ]
    return iv_ranges

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
