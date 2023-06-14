"""BDSP Seed Finder module for pyodide to access"""
from functools import reduce
from importlib import resources as importlib_resources
import sys
import numpy as np
from . import resources

# def mat_xorshift128():
#     ...
# https://github.com/Lincoln-LM/RNG-Python-Scripts/blob/0f726e02edd10d0e9c4e2379e2c7874d0ab1f5da/rng_related/xorshift_state_recovery.py#L15
# XORSHIFT128 = mat_xorshift128()
XORSHIFT128 = np.load(
    importlib_resources.files(resources).joinpath("xorshift_matrix.npy")
)


def main():
    """Main function to be run for the bdsp_seed_finder module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from bdsp seed finder!")
    print(f"{sys.version=}")


def mat_inverse(mat):
    """Compute the inverse of a GF(2) matrix via gauss jordan elimination"""
    height, width = mat.shape

    res = np.identity(height, np.uint8)
    pivot = 0
    for i in range(width):
        isfound = False
        for j in range(i, height):
            if mat[j, i]:
                if isfound:
                    mat[j] ^= mat[pivot]
                    res[j] ^= res[pivot]
                else:
                    isfound = True
                    mat[[j, pivot]] = mat[[pivot, j]]
                    res[[j, pivot]] = res[[pivot, j]]
        if isfound:
            pivot += 1

    for i in range(width):
        assert mat[i, i]

    for i in range(1, width)[::-1]:
        for j in range(i)[::-1]:
            if mat[j, i]:
                mat[j] ^= mat[i]
                res[j] ^= res[i]
    return res[:width]


def state_to_observations(intervals: tuple[int]) -> np.ndarray:
    """Build a matrix to convert bitvec of the rng state to a bitvec of the observations"""
    state_mat = np.identity(128, np.uint8)

    observations_mat = np.zeros((4 * 39, 128), np.uint8)
    for i, interval in enumerate(intervals):
        observations_mat[4 * i : 4 * (i + 1)] = state_mat[-4:]
        for _ in range(interval):
            state_mat = (XORSHIFT128 @ state_mat) & 1

    return observations_mat


def calc_seed(inputs: tuple[tuple[float, int]]) -> int:
    """Calculate seed from inputs"""
    if len(inputs) < 39:
        return None
    inputs = inputs[:39]

    observations = np.zeros((39 * 4, 1), np.uint8)
    intervals = []

    last_time = inputs[0][0]
    for i, (time, blink_type) in enumerate(inputs):
        observations[3 + i * 4] = blink_type
        intervals.append(round(time - last_time))

    state_to_observations_mat = state_to_observations(intervals)
    observations_to_state_mat = mat_inverse(state_to_observations_mat)

    state = (observations_to_state_mat @ observations) & 1
    state_int = reduce(lambda p, q: (int(p) << 1) | int(q), (x[0] for x in state))
    result_seed0 = state_int >> 96
    result_seed1 = (state_int >> 64) & 0xFFFFFFFF
    result_seed2 = (state_int >> 32) & 0xFFFFFFFF
    result_seed3 = state_int & 0xFFFFFFFF

    print(
        f"{result_seed0=:08X} {result_seed1=:08X} {result_seed2=:08X} {result_seed3=:08X}"
    )

    return f"{result_seed0=:08X} {result_seed1=:08X} {result_seed2=:08X} {result_seed3=:08X}"
