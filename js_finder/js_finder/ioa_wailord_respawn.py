"""SWSH npc calibration module for pyodide to access"""
from importlib import resources as importlib_resources
import sys
import numpy as np
from numba_pokemon_prngs.xorshift.xoroshiro128plus import Xoroshiro128PlusRejection
from . import resources


def generate_results(
    seed_0: int,
    seed_1: int,
    npc_count: int,
    min_advance: int,
    max_advance: int,
):
    results = ""
    rng = Xoroshiro128PlusRejection(np.uint64(seed_0), np.uint64(seed_1))
    go = Xoroshiro128PlusRejection(0, 0)
    for advance in range(min_advance, max_advance):
        go.re_init(rng.state[0], rng.state[1])
        for _ in range(npc_count):
            go.next_rand(91)
        for _ in range(5):
            go.next_rand(51)
        for _ in range(3):
            go.next_rand(45)
            go.next_rand(10)
        if go.next_rand(100) == 0:
            results += f"<tr><td>{advance}</td></tr>"
        rng.next()
    return results


def main():
    """Main function to be run for the ioa_wailord_respawn module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from ioa wailord respawn!")
    print(f"{sys.version=}")
