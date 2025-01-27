from math import floor

def frame_to_ms(frame):
    return floor((frame) / (16777216 / 280896) * 1000)
