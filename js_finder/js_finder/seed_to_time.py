"""Seed to Time module for pyodide to access"""
import sys
import numpy as np
from numba_pokemon_prngs import mersenne_twister


def main():
    """Main function to be run for the seed_to_time module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from seed to time!")
    print(f"{sys.version=}")


def test_coinflip(target_seed: np.uint32, coinflip_seq: str) -> str:
    """Test the coinflips for a target seed"""
    target_seed = np.uint32(target_seed)
    coinflip_seq = tuple(int(flip) for flip in coinflip_seq)

    seed_high = target_seed >> np.uint32(24)
    seed_hour = (target_seed >> np.uint32(16)) & np.uint32(0xFF)
    seed_delay = target_seed & np.uint32(0xFFFF)

    test_seed_hour = np.uint32(seed_hour)
    results = []
    for second in range(-2, 3):
        test_seed_high = (seed_high + np.uint32(second)) & np.uint32(0xFF)
        for delay in range(-200, 201):
            test_seed_delay = (seed_delay + np.uint32(delay)) & np.uint32(0xFFFFFFFF)
            test_seed = (
                (test_seed_high << np.uint32(24))
                | (test_seed_hour << np.uint32(16))
                | test_seed_delay
            )
            rng = mersenne_twister.MersenneTwister(test_seed)
            if all((rng.next() & 1) == flip for flip in coinflip_seq):
                rng = mersenne_twister.MersenneTwister(test_seed)
                flips = "".join(str(rng.next() & 1) for _ in range(12))
                results.append(
                    f"{test_seed = :08X} is valid! {test_seed_delay = } {flips = }"
                )
    return "<br />".join(results)
