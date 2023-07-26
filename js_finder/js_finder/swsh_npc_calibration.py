"""SWSH npc calibration module for pyodide to access"""
from importlib import resources as importlib_resources
import sys
import numpy as np
from numba_pokemon_prngs.xorshift.xoroshiro128plus import Xoroshiro128PlusRejection
from . import resources


# TODO: info on construction
XOROSHIRO_RECOVERY = np.load(
    importlib_resources.files(resources).joinpath("xoroshiro_state_recovery.npy")
)

def find_seed(motions_str: str):
    """Find seed of main rng"""
    if len(motions_str) < 128:
        return "Not enough motions recorded"
    state = np.zeros(2, np.uint64)
    for i, motion in enumerate(motions_str[:128]):
        if motion == "1":
            state ^= XOROSHIRO_RECOVERY[i]
    rng = Xoroshiro128PlusRejection(*state)
    rng.advance(len(motions_str))

    return f"Seed 0: {rng.state[0]:X} Seed 1: {rng.state[1]:X}"

def find_advance(
    motions_str: str,
    min_advance: int,
    max_advance: int,
    seed_0: int,
    seed_1: int
):
    """Find current advance of main rng"""
    motions = tuple(map(int, motions_str))

    rng = Xoroshiro128PlusRejection(np.uint64(seed_0), np.uint64(seed_1))
    rng.advance(min_advance)
    matching_advances = []
    for advance in range(min_advance, max_advance + 1):
        matching_count = 0
        go = Xoroshiro128PlusRejection(*rng.state)
        while go.next_rand(2) == motions[matching_count]:
            matching_count += 1
            if matching_count == len(motions):
                print(advance, matching_count)
                matching_advances.append(advance + matching_count)
                break
        rng.next()
    return "Possible Advances:<br>" + "<br>".join(
        f"Before motions: {matching_advance - len(motions)} After motions: {matching_advance}"
        for matching_advance
        in matching_advances
    )

def find_npc(
    data: list[list[int]],
    min_npcs: int,
    max_npcs: int,
    seed_0: int,
    seed_1: int
):
    """Find npc count of area"""
    possible_npcs = set(range(min_npcs, max_npcs + 1))
    for menu_exit, menu_enter in data:
        for npc_count in possible_npcs.copy():
            rng = Xoroshiro128PlusRejection(np.uint64(seed_0), np.uint64(seed_1))
            rng.advance(menu_exit)
            rng_count = Xoroshiro128PlusRejection(*rng.state)
            for _ in range(npc_count):
                rng.next_rand(91)
            rng.next()
            rng.next_rand(60)
            advance = menu_exit
            while not np.all(rng_count.state == rng.state):
                rng_count.next()
                advance += 1
            if advance != menu_enter:
                possible_npcs.remove(npc_count)
    return f"Possible NPCs: {possible_npcs}"

def main():
    """Main function to be run for the swsh_npc_calibration module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from swsh npc calibration!")
    print(f"{sys.version=}")
