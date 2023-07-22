"""BDSP Coin Flip module for pyodide to access"""
from importlib import resources as importlib_resources
import sys
from functools import reduce
import numpy as np
from numba_pokemon_prngs.xorshift.xorshift128 import Xorshift128
from . import resources
from .util.matrix import mat_inverse, inverse_proress

# def mat_xorshift128():
#     ...
# https://github.com/Lincoln-LM/RNG-Python-Scripts/blob/0f726e02edd10d0e9c4e2379e2c7874d0ab1f5da/rng_related/xorshift_state_recovery.py#L15
# XORSHIFT128 = mat_xorshift128()
# TODO: use little bit order matrix rather than big bit order
XORSHIFT128 = np.load(
    importlib_resources.files(resources).joinpath("xorshift_matrix.npy")
)


def mat_state_to_observations(intervals: list[int]) -> np.ndarray:
    """Build a matrix that maps the rng state to observations based on the given intervals"""

    state_mat = np.identity(128, np.uint8)
    observation_mat = np.zeros((len(intervals), 128), np.uint8)

    for i, interval in enumerate(intervals[1:]):
        observation_mat[i] = state_mat[-1:]
        for _ in range(interval):
            state_mat = (state_mat @ XORSHIFT128) & 1

    return observation_mat

def solve(intervals: list[int], observations: list[int]) -> list[int]:
    """Solve for the state of the rng based on the given intervals and observations"""

    observations = np.array([[x] for x in observations], np.uint8)

    state_to_observations_mat = mat_state_to_observations(intervals)
    observations_to_state_mat = mat_inverse(state_to_observations_mat)

    state = (observations_to_state_mat @ observations) & 1
    state_int = reduce(lambda p, q: (int(p) << 1) | int(q), (x[0] for x in state))

    result_seed0 = state_int >> 96
    result_seed1 = (state_int >> 64) & 0xFFFFFFFF
    result_seed2 = (state_int >> 32) & 0xFFFFFFFF
    result_seed3 = state_int & 0xFFFFFFFF

    rng = Xorshift128(result_seed0, result_seed1, result_seed2, result_seed3)
    rng.advance(sum(intervals[1:]))

    return f"{rng.state[0]:08X} {rng.state[1]:08X} {rng.state[2]:08X} {rng.state[3]:08X}"

def progress(intervals: list[int]):
    """Estimate the amount of flips needed to compute the state"""
    interval_count = len(intervals)
    bits_known, total_bits = inverse_proress(mat_state_to_observations(intervals))

    flips_needed = min(round(interval_count/bits_known*total_bits), 140) if bits_known else 140

    return int(bits_known), (
        f"Flip Count: {interval_count}<br>"
        f"Seed Progress: {bits_known}/{total_bits}<br>"
        f"Estimated Flips Left: {flips_needed - interval_count}"
    )

def main():
    """Main function to be run for the bdsp_coin_flip module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from bdsp coin flip!")
    print(f"{sys.version=}")
