"""Ten Lines module for pyodide to access"""

from importlib import resources as importlib_resources
from math import floor
from itertools import cycle
import sys
import datetime
import json
from typing import Collection, Iterable
import numpy as np
from . import resources

# mults/adds for jumping 2^i LCRNG advances
JUMP_DATA = (
    # (mult, add)
    (0x41C64E6D, 0x6073),
    (0xC2A29A69, 0xE97E7B6A),
    (0xEE067F11, 0x31B0DDE4),
    (0xCFDDDF21, 0x67DBB608),
    (0x5F748241, 0xCBA72510),
    (0x8B2E1481, 0x1D29AE20),
    (0x76006901, 0xBA84EC40),
    (0x1711D201, 0x79F01880),
    (0xBE67A401, 0x8793100),
    (0xDDDF4801, 0x6B566200),
    (0x3FFE9001, 0x803CC400),
    (0x90FD2001, 0xA6B98800),
    (0x65FA4001, 0xE6731000),
    (0xDBF48001, 0x30E62000),
    (0xF7E90001, 0xF1CC4000),
    (0xEFD20001, 0x23988000),
    (0xDFA40001, 0x47310000),
    (0xBF480001, 0x8E620000),
    (0x7E900001, 0x1CC40000),
    (0xFD200001, 0x39880000),
    (0xFA400001, 0x73100000),
    (0xF4800001, 0xE6200000),
    (0xE9000001, 0xCC400000),
    (0xD2000001, 0x98800000),
    (0xA4000001, 0x31000000),
    (0x48000001, 0x62000000),
    (0x90000001, 0xC4000000),
    (0x20000001, 0x88000000),
    (0x40000001, 0x10000000),
    (0x80000001, 0x20000000),
    (0x1, 0x40000000),
    (0x1, 0x80000000),
)


def distance(state0: int, state1: int) -> int:
    """Efficiently compute the distance from LCRNG state0 -> state1"""
    mask = 1
    dist = 0

    for mult, add in JUMP_DATA:
        if state0 == state1:
            break

        if (state0 ^ state1) & mask:
            state0 = (state0 * mult + add) & 0xFFFFFFFF
            dist += mask

        mask <<= 1

    return dist


# base seed is an arbitrary starting point, it can be anything as long as it is consistent
BASE_SEED = 0
DATA = np.load(importlib_resources.files(resources).joinpath("generated/ten_lines_precalc.npy"))
RTC_DATA = np.load(importlib_resources.files(resources).joinpath("generated/rtc_data.npy"))


with open(
    importlib_resources.files(resources).joinpath("generated/frlg_seeds.json"),
    "r",
    encoding="utf-8",
) as frlg_seeds:
    FRLG_DATA = json.load(frlg_seeds)


def get_data_date():
    """Get the timestamp of the FRLG seed data"""
    return FRLG_DATA["time_stamp"]


def filter_frlg(
    seeds: np.ndarray,
    result_count: int,
    game: str,
) -> Iterable[Collection[np.uint32 | str]]:
    """Filter a list of seeds for the first result_count seeds possible in FRLG"""
    seeds = cycle(seeds)
    i = 0
    while i < result_count:
        data = next(seeds)
        (advance, seed) = data
        for sound, data in FRLG_DATA[game].items():
            for l, data in data.items():
                for button, data in data.items():
                    for held, data in data.items():
                        data = data.get(
                            str(seed), None
                        )
                        if data is not None:
                            yield (
                                advance,
                                seed,
                                data[0],
                                f"{sound=}, {l=}, {button=}, {held=}",
                            )
                            i += 1
                            if i >= result_count:
                                return


def filter_rtc(
    seeds: np.ndarray,
    result_count: int,
) -> Iterable[Collection[np.uint32 | str]]:
    """Filter a list of RTC value seeds for the first result_count that are actually early"""
    seeds = cycle(seeds)
    i = 0
    while i < result_count:
        data = next(seeds)
        (sort_value, seed_time, seed) = data
        advance = sort_value - seed_time
        # the find_initial_seeds algorithm breaks down when attempting to sort by a value that is offset from the actual distance
        # since it relies on the lcg distance working mod 2^32.
        # the only values that break the algorithm are those with advance + seed_time >= 2^32 and thus can be assumed to be undesireable.
        # filtering these out leaves only the values that are properly sorted
        if int(advance) + int(seed_time) < 0x100000000:
            yield (advance, seed, seed_time, "")
            i += 1


def ten_lines(
    target_seed: int, result_count: int, game: str
) -> Iterable[Collection[np.uint32 | str]]:
    """Efficiently find the closest initial seeds up to result_count results"""
    if game == "painting":
        return (
            (advance, seed, seed, "")
            for (advance, seed) in find_initial_seeds(target_seed, result_count)
        )
    elif game == "rtc":
        return filter_rtc(find_initial_seeds(target_seed, result_count=RTC_DATA.shape[0], data=RTC_DATA), result_count)
    return filter_frlg(find_initial_seeds(target_seed), result_count, game)


def find_initial_seeds(target_seed: int, result_count: int = 0x10000, data: np.ndarray = DATA) -> np.ndarray:
    """Efficiently sort all possible initial seeds by those closest to a target seed"""
    # by adding the distance from initial -> base seed + the distance from base seed -> target seed,
    # the result is the distance from initial -> target seed

    # compute the distance from base seed -> target seed
    distance_from_base = distance(BASE_SEED, target_seed)

    # when doing this addition, overflow only happens
    # when (initial -> base) + (base -> target) > 0xFFFFFFFF
    # the lowest seed that overflows is guaranteed to be the closest seed to our target
    # this is true unless no seeds overflow, in which case, the closest seed is always DATA[0]
    # this comparison is equivalent to (initial -> base) > 0xFFFFFFFF - (base -> target)
    target = 0xFFFFFFFF - distance_from_base
    # binary search for lowest (initial -> base) that is > target
    left = 0
    right = np.shape(data)[0] - 1
    while left < right:
        middle = (left + right) // 2
        if data[middle, 0] <= target:
            left = middle + 1
        else:
            right = middle

    # if no result was found, default to DATA[0]
    result_index = left if data[left, 0] > target else 0

    # TODO: is np.roll better with result_count=np.shape(data)[0]
    # take a wrapping slice with length result_count
    wrap_count = max(result_index + result_count - np.shape(data)[0], 0)
    result = np.empty((result_count, data.shape[1]), np.uint32)
    result[: result_count - wrap_count] = data[
        result_index : result_index + result_count
    ]
    if wrap_count:
        result[-wrap_count:] = data[:wrap_count]
    # store initial -> target
    result[:, 0] += distance_from_base

    return result


def main():
    """Main function to be run for the ten_lines module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from ten lines!")
    print(f"{sys.version=}")


def run_ten_lines(target_seed: int, num_results: int, game: str) -> str:
    """Run ten lines to find origin seeds"""
    # no longer actually 10 lines

    return "".join(
        (
            "<tr>"
            f"<td>{seed}</td>"
            f"<td>{seed:04X}</td>"
            f"<td>{advance}</td>"
            f"<td>{floor(seed_frame + advance)}</td>"
            f"<td>{datetime.timedelta(seconds=floor((seed_frame + advance) / (16777216 / 280896)))}</td>"
            + (
                f"<td>{floor((seed_frame) / (16777216 / 280896) * 1000)}ms</td>"
                if game != "rtc"
                else
                f"<td>{datetime.datetime(year=2000, month=1, day=1)+datetime.timedelta(seconds=seed_frame/60)}"
                f" | {datetime.timedelta(seconds=seed_frame/60)}</td>"
            )
            + f"<td>{info}</td>"
            "</tr>"
        )
        for (advance, seed, seed_frame, info) in ten_lines(
            target_seed, num_results, game
        )
    )
