"""VC Gen 2 RNG prediction"""

class DivCounter:
    """Individual rDIV predictor
    https://github.com/zaksabeast/VC-RNG-Tool/blob/main/vc_rng_lib/src/div.rs"""

    DIV_PATTERN = (
        0x12,
        0x12,
        0x12,
        0x13,
        0x12,
        0x12,
        0x13,
        0x12,
        0x12,
        0x13,
        0x12,
        0x12,
        0x13,
        0x12,
        0x12,
        0x13,
    )
    ADJUSTED_INDEXES = (
        {0x562, 0x563, 0x22B5, 0x22B6},
        {0x8, 0x9, 0x562, 0x563, 0x22B5, 0x22B6},
        {0x8, 0x9, 0x562, 0x563, 0x1D5B, 0x1D5C, 0x22B5, 0x22B6},
    )

    def __init__(self, cycle_index: int, value: int, div_type: int):
        self.cycle_index = cycle_index
        self.value = value
        self.div_type = div_type

    def get_increment(self, cycle_index: int):
        """Get the expected increment for the given cycle index"""
        expected_value = self.DIV_PATTERN[cycle_index & 0xF]
        if cycle_index in self.ADJUSTED_INDEXES[self.div_type]:
            expected_value = 0x12 if expected_value == 0x13 else 0x13
        return expected_value

    def next(self):
        """Step the DIV counter forwards"""
        increment = self.get_increment(self.cycle_index)
        self.value = (self.value + increment) & 0xFF
        self.cycle_index = (self.cycle_index + 1) & 0x3FFF

    def previous(self):
        """Step the DIV counter backwards"""
        self.cycle_index = (self.cycle_index - 1) & 0x3FFF
        last_increment = self.get_increment(self.cycle_index)
        self.value = (self.value - last_increment) & 0xFF


class Gen2RNG:
    """Basic Gen 2 RNG predictor
    https://github.com/zaksabeast/VC-RNG-Tool/blob/main/vc_rng_lib/src/rng.rs"""

    def __init__(
        self, advance: int, state: int, add_div: DivCounter, sub_div: DivCounter
    ):
        self.advance = advance
        self.add_rng = state >> 8
        self.sub_rng = state & 0xFF
        self.add_div = add_div
        self.sub_div = sub_div

    @classmethod
    def from_tuple(cls, data: tuple):
        """Create a Gen2RNG object from a tuple"""
        return cls(data[0], data[1], DivCounter(*data[2]), DivCounter(*data[3]))

    @property
    def state(self):
        """Get the full state of the RNG"""
        return (self.add_rng << 8) | self.sub_rng

    def next(self):
        """Step the RNG forwards"""
        self.add_div.next()
        self.sub_div.next()
        add_result = self.add_rng + self.add_div.value
        self.add_rng = add_result & 0xFF
        self.sub_rng = (self.sub_rng - (self.sub_div.value + (add_result >> 8))) & 0xFF
        self.advance += 1

    def previous(self):
        """Step the RNG backwards"""
        self.add_rng = (self.add_rng - self.add_div.value) & 0xFF
        add_result = self.add_rng + self.add_div.value
        self.sub_rng = (self.sub_rng + (self.sub_div.value + (add_result >> 8))) & 0xFF
        self.add_div.previous()
        self.sub_div.previous()
        self.advance -= 1
