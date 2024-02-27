"""Stadium 2 decoration odds module for pyodide to access"""
import sys


def main():
    """Main function to be run for the stadium2_decoration_odds module"""
    print("Hello from stadium 2 decoration odds!")
    print(f"{sys.version=}")


class Stad2LCRNG:
    """Stadium 2 LCRNG"""

    def __init__(self, seed: int):
        self.seed = seed

    def next(self, mask: int = None):
        self.seed = ((self.seed * 0xD) + 0x5F) & 0xFF
        return self.seed & (mask or 0xFF)

    def next_compare(self, value: int):
        return self.next() < value


def calculate(tid: int):
    """Calculate odds for each decoration"""
    data = {decoration_id: 0 for decoration_id in range(37)}
    for seed in range(256):
        rng = Stad2LCRNG(seed)
        if rng.next_compare(36):
            if rng.next_compare(72):
                if rng.next_compare(72):
                    # only ever 164
                    # rand = rng.next()
                    # if rand < 77:
                    #     # tentacool doll or pikachu bed depending on if round 2 is unlocked
                    # elif rand < 154:
                    #     # tentacool doll
                    # else:
                    data[32 + bool(tid & (1 << 7))] += 1
                else:
                    data[24 + ((tid >> 4) & 7)] += 1
            else:
                rand = rng.next(3)
                data[16 + (rand << 1) + bool(tid & (1 << rand))] += 1
        else:
            rand = rng.next(7)
            data[(rand << 1) + bool(tid & (1 << rand + 8))] += 1

    return (
        "".join(
            f"<tr><td>{decoration_id}</td><td>{weight}/256</td><td>{weight/2.56:.02f}%</td></tr>"
            for decoration_id, weight in data.items()
        )
        or "<tr><td>Invalid Target Seed!</td></tr>"
    )
