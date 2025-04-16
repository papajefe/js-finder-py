from math import floor

SYSTEM_TIMING_DATA = {
    "RSE": {"frame_rate": 16777216 / 280896, "offset_ms": 0},
    "GBA": {"frame_rate": 16777216 / 280896, "offset_ms": -260},
    "GBP": {"frame_rate": 16777216 / 280896, "offset_ms": 200},
    "NDS": {"frame_rate": 16756991 / 280896, "offset_ms": 788},
    "3DS": {"frame_rate": 16756991 / 280896, "offset_ms": 1558},
}


def frame_to_ms(frame: int, system: str = "RSE"):
    """Convert frame to milliseconds based on the selected system"""
    return (
        floor(frame / SYSTEM_TIMING_DATA[system]["frame_rate"] * 1000)
        + SYSTEM_TIMING_DATA[system]["offset_ms"]
    )
