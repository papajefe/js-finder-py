"""VC Crystal TID module for pyodide to access"""

import sys
import numpy as np
from .g2_rng import Gen2RNG


def main():
    """Main function to be run for the crystal_tid module"""
    np.seterr(over="ignore", under="ignore")
    print("Hello from crystal tid!")
    print(f"{sys.version=}")

TID_DATA = (
    (327, 0xAD77, (13751, 0x1F, 0), (13038, 0x1F, 1)),
    (424, 0x6778, (2339, 0xC8, 0), (1626, 0xC9, 1)),
    (521, 0xF7A7, (1118, 0x71, 1), (405, 0x71, 1)),
    (618, 0x95C6, (6747, 0x1A, 1), (6034, 0x1A, 1)),
    (715, 0x36E3, (11006, 0xC3, 1), (10293, 0xC3, 1)),
    (812, 0x27AC, (15978, 0x6D, 1), (15265, 0x6D, 1)),
    (909, 0x6929, (4566, 0x16, 1), (3853, 0x17, 1)),
    (1006, 0xFD55, (9538, 0xC0, 1), (8825, 0xC0, 1)),
    (1103, 0xE229, (14510, 0x6A, 1), (13797, 0x6A, 1)),
    (1200, 0x1AAE, (3098, 0x14, 1), (2385, 0x14, 1)),
    (1297, 0xA3E6, (8070, 0xBD, 1), (7357, 0xBE, 1)),
    (1394, 0x7EC7, (13042, 0x67, 1), (12329, 0x67, 1)),
    (1491, 0xAA53, (1630, 0x11, 1), (917, 0x11, 1)),
    (1588, 0xE2DC, (14766, 0xBA, 1), (14053, 0xBA, 1)),
    (1685, 0x2952, (4011, 0x63, 1), (3298, 0x63, 1)),
    (1782, 0x73C4, (8270, 0x0C, 1), (7557, 0x0C, 1)),
    (1879, 0xCC29, (13899, 0xB5, 1), (13186, 0xB5, 1)),
    (1976, 0x7540, (2487, 0x5F, 1), (1774, 0x5F, 1)),
    (2073, 0x6F02, (7459, 0x08, 1), (6746, 0x09, 1)),
    (2170, 0xBB75, (12431, 0xB2, 1), (11718, 0xB2, 1)),
    (2267, 0x5998, (1019, 0x5C, 0), (7813, 0x5C, 2)),
    (2364, 0x496C, (5991, 0x06, 0), (12785, 0x06, 2)),
    (2461, 0x8AF1, (5651, 0xAF, 0), (12445, 0xB0, 2)),
    (2558, 0x1C1E, (10623, 0x59, 0), (1033, 0x59, 2)),
    (2655, 0xFBFE, (6718, 0x03, 1), (6005, 0x03, 1)),
    (2752, 0xE5D4, (3470, 0xAC, 1), (2757, 0xAC, 1)),
    (2849, 0xDE97, (9099, 0x55, 0), (8386, 0x55, 1)),
    (2946, 0xDA55, (13358, 0xFE, 1), (12645, 0xFE, 1)),
    (3043, 0xE50D, (2603, 0xA7, 0), (1890, 0xA7, 1)),
    (3140, 0x4070, (7575, 0x51, 0), (6862, 0x51, 1)),
    (3237, 0xEC7F, (12547, 0xFA, 0), (11834, 0xFB, 1)),
)

def search(search_tid: int, inaccuracy_leeway: bool, min_vframe: int, max_vframe: int, min_reopen: int, max_reopen: int) -> str:
    """Search for advances/vframes potentially producing the target tid"""
    min_reopen = max(min_reopen, 0)
    max_reopen = min(max_reopen, 30)
    rows = ""
    for reopen in range(min_reopen, max_reopen + 1):
        lag_frames = (reopen+1) * 11
        rng = Gen2RNG.from_tuple(TID_DATA[reopen])
        # align rng to the 4 frame input window
        for _ in range(3):
            rng.next()
        # frames that pass between A press and tid generation
        rng.advance -= 17
        while rng.advance + lag_frames < min_vframe:
            rng.next()
        while rng.advance + lag_frames <= max_vframe:
            # attempt to simulate tid generation
            # this is not 100% accurate
            # https://github.com/pret/pokecrystal/blob/4d6c3e2975037f03b9b859db3ad15976af6b7539/engine/menus/intro_menu.asm#L120-L128
            tid = rng.sub_rng << 8
            rng.next()
            tid |= rng.add_rng
            rng.previous()
            matches = tid == search_tid
            if inaccuracy_leeway:
                search_low = search_tid & 0xFF
                search_high = search_tid >> 8
                tid_low = tid & 0xFF
                tid_high = tid >> 8
                matches |= (
                    tid_low in ((search_low - 1) & 0xFF, search_low, (search_low + 1) & 0xFF)
                    and tid_high in ((search_high - 1) & 0xFF, search_high, (search_high + 1) & 0xFF)
                )
            if matches:
                rows += (
                    "<tr>"
                    f"<td>{tid}</td>"
                    f"<td>{reopen}</td>"
                    f"<td>{rng.advance}</td>"
                    f"<td>{rng.advance + lag_frames}</td>"
                    "</tr>"
                )
            # move to next input window
            for _ in range(4):
                rng.next()

    return rows
