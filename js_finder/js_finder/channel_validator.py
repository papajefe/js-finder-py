"""Channel Validator module for pyodide to access"""
import sys
import numpy as np
from numba_pokemon_prngs.lcrng import XDRNG, XDRNGR


def main():
    """Main function to be run for the channel_validator module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from channel validator!")
    print(f"{sys.version=}")


def validate_jirachi(seed, post_menu: bool = False) -> set[int]:
    """Find all valid menu seeds for a target final seed"""
    valid_seeds = set()
    if post_menu:
        seed = do_pre_menu(seed)
    rng = XDRNGR(seed)
    num1 = rng.next_u16()
    num2 = rng.next_u16()
    num3 = rng.next_u16()
    rng.advance(3)
    if num1 <= 0x4000:  # 6 advances
        valid_seeds.update(validate_menu(rng.seed))
    rng.advance(1)
    if num2 > 0x4000 and num1 <= 0x547A:  # 7 advances
        valid_seeds.update(validate_menu(rng.seed))
    rng.advance(1)
    if num3 > 0x4000 and num2 > 0x547A:  # 8 advances
        valid_seeds.update(validate_menu(rng.seed))
    return valid_seeds

def do_pre_menu(seed) -> int:
    """Advance a seed past the menu sequence"""
    rng = XDRNG(seed)
    mask = 0
    while mask < 14:
        mask |= 1 << (rng.next_u16() >> 14)
    rng.advance(4)
    if rng.next_u16() <= 0x4000 or rng.next_u16() <= 0x547A:
        rng.advance(1)
    else:
        rng.advance(2)
    return rng.seed

def validate_menu(seed) -> set[int]:
    """Find all valid menu seeds for a target jirachi seed"""
    valid_menu_seeds = set()
    rng = XDRNGR(seed)
    target = seed >> 30
    if target == 0:
        return valid_menu_seeds
    mask = 1 << target
    shift = 0
    # if we reverse to a seed that gives our target shift,
    # any valid seed prior to it cannot end on our target
    # as it will already have that bit of the mask filled
    while shift != target:
        seed = rng.next()
        # a seed is only valid if when starting from said seed
        # we can fill in the entire mask and end with our target
        if (mask & 0b1110) == 0b1110:
            valid_menu_seeds.add(seed)
        shift = seed >> 30
        mask |= 1 << shift
    return valid_menu_seeds


def validate_channel(target_seed: int, post_menu: bool = False) -> str:
    """Run validation to find all fully valid seeds for a given channel jirachi seed"""

    return (
        "".join(
            f"<tr><td>{seed:08X}</td></tr>" for seed in validate_jirachi(target_seed, post_menu)
        )
        or "<tr><td>Invalid Target Seed!</td></tr>"
    )
