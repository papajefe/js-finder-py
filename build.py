"""Additional setup to be run by build.sh"""

from datetime import datetime, timedelta
import csv
import json
import requests
import numpy as np


BASE_SEED = 0

FR_ENG_SHEET = "https://docs.google.com/spreadsheets/d/1Mf3F4kTvNEYyDGWKVmMSiar3Fwh1PLzWVXUvGx9YxfA/gviz/tq?tqx=out:csv&sheet=Fire%20Red%20Raw%20Seed%20Data"
LG_ENG_SHEET = "https://docs.google.com/spreadsheets/d/12TUcXGbLY_bBDfVsgWZKvqrX13U6XAATQZrYnzBKP6Y/gviz/tq?tqx=out:csv&sheet=Leaf%20Green%20Seeds"

FR_JPN_1_0_SHEET = "https://docs.google.com/spreadsheets/d/1GMRFM1obLDcYbR6GR6KrE8UZotA7djUTw8PxqVFnCVY/gviz/tq?tqx=out:csv&sheet=JPN%20Fire%20Red%201.0%20Seeds"
FR_JPN_1_1_SHEET = "https://docs.google.com/spreadsheets/d/1aQeWaZSi1ycSytrNEOwxJNoEg-K4eItYagU_dh9VIeU/gviz/tq?tqx=out:csv&sheet=JPN%20Fire%20Red%201.0%20Seeds"

LG_JPN_SHEET = "https://docs.google.com/spreadsheets/d/1LSRVD0_zK6vyd6ettUDfaCFJbm00g451d8s96dqAbA4/gviz/tq?tqx=out:csv&sheet=JPN%20Leaf%20Green%20Seeds"

EU_OFFSETS = {
    "lr": {"yes": -9, "no": -8},
    "la": {"yes": 8, "no": -1},
    "help": {"yes": 7, "no": 0},
}

FR_JPN_OFFSETS = {
    "lr": 0,
    "la": -1,
    "help": 7,
}


def pull_frlg_seeds():
    """Pull FRLG seed from spreadsheet"""
    time_stamp = datetime.now()
    frlg_seeds = {
        "time_stamp": str(time_stamp),
    } | {
        game: {
            sound: {
                l: {
                    button: {select: {} for select in ("yes", "no")}
                    for button in ("a", "start") + (("l",) if l == "la" else ())
                }
                for l in ("la", "help", "lr")
            }
            for sound in ("stereo", "mono")
        }
        for game in ("fr", "fr_eu", "fr_jpn_1_0", "fr_jpn_1_1", "lg", "lg_eu", "lg_jpn")
    }

    sheet_txt = requests.get(
        FR_ENG_SHEET,
        timeout=5,
    ).text
    sheet_csv = csv.reader(sheet_txt.split("\n"))
    for i, row in enumerate(sheet_csv):
        if i == 0:
            continue
        if row[0]:
            program_frame_str = row[0]
            program_frame = int(program_frame_str)

            def add_seed(col, sound, l, button):
                seed_str = row[col]
                if seed_str and seed_str != "-":
                    seed = int(seed_str, 16)
                    if seed < 0x10000:
                        frlg_seeds["fr"][sound][l][button]["no"][seed] = (
                            program_frame / 2
                        )
                        frlg_seeds["fr"][sound][l][button]["yes"][
                            (seed + (7 if l == "help" else -1)) & 0xFFFF
                        ] = (program_frame / 2)
                        frlg_seeds["fr_eu"][sound][l][button]["no"][
                            seed + EU_OFFSETS[l]["no"]
                        ] = (program_frame / 2)
                        frlg_seeds["fr_eu"][sound][l][button]["yes"][
                            seed + EU_OFFSETS[l]["yes"]
                        ] = (program_frame / 2)

            add_seed(3, "stereo", "la", "a")
            add_seed(7, "stereo", "help", "a")
            add_seed(11, "stereo", "lr", "a")
            add_seed(15, "mono", "la", "a")
            add_seed(19, "mono", "help", "a")
            add_seed(23, "mono", "lr", "a")
            add_seed(27, "mono", "lr", "start")
            add_seed(31, "mono", "la", "start")
            add_seed(35, "mono", "help", "start")
            add_seed(39, "stereo", "help", "start")
            add_seed(43, "stereo", "lr", "start")
            add_seed(47, "stereo", "la", "start")
            add_seed(51, "stereo", "la", "l")
            add_seed(54, "mono", "la", "l")

    sheet_txt = requests.get(
        LG_ENG_SHEET,
        timeout=5,
    ).text
    sheet_csv = csv.reader(sheet_txt.split("\n"))
    for i, row in enumerate(sheet_csv):
        if i == 0:
            continue
        if row[0]:
            frame = int(row[0]) + 4062 / 2

            def add_seed(col, sound, l, button):
                seed = int(row[col], 16)
                frlg_seeds["lg"][sound][l][button]["no"][seed] = frame
                frlg_seeds["lg"][sound][l][button]["yes"][
                    (seed + (7 if l == "help" else -1)) & 0xFFFF
                ] = frame
                frlg_seeds["lg_eu"][sound][l][button]["no"][
                    (seed + EU_OFFSETS[l]["no"]) & 0xFFFF
                ] = frame
                frlg_seeds["lg_eu"][sound][l][button]["yes"][
                    (seed + EU_OFFSETS[l]["yes"]) & 0xFFFF
                ] = frame

            add_seed(3, "mono", "lr", "a")
            add_seed(4, "mono", "la", "a")
            add_seed(5, "mono", "help", "a")
            add_seed(6, "stereo", "lr", "a")
            add_seed(7, "stereo", "la", "a")
            add_seed(8, "stereo", "help", "a")

    sheet_txt = requests.get(
        FR_JPN_1_0_SHEET,
        timeout=5,
    ).text
    sheet_csv = csv.reader(sheet_txt.split("\n"))
    for i, row in enumerate(sheet_csv):
        if i == 0:
            continue
        if row[0]:
            frame = int(row[0])

            def add_seed(col, sound, l, button):
                if row[col]:
                    seed = int(row[col], 16)
                    frlg_seeds["fr_jpn_1_0"][sound][l][button]["no"][seed] = frame
                    frlg_seeds["fr_jpn_1_0"][sound][l][button]["yes"][
                        (seed + FR_JPN_OFFSETS[l]) & 0xFFFF
                    ] = frame

            add_seed(1, "mono", "lr", "a")
            add_seed(2, "mono", "la", "a")
            add_seed(3, "mono", "help", "a")
            add_seed(4, "stereo", "lr", "a")
            add_seed(5, "stereo", "la", "a")
            add_seed(6, "stereo", "help", "a")

    sheet_txt = requests.get(
        FR_JPN_1_1_SHEET,
        timeout=5,
    ).text
    sheet_csv = csv.reader(sheet_txt.split("\n"))
    for i, row in enumerate(sheet_csv):
        if i < 3:
            continue
        if row[0]:
            frame = int(row[0])

            def add_seed(col, sound, l, button):
                if row[col]:
                    seed = int(row[col], 16)
                    frlg_seeds["fr_jpn_1_1"][sound][l][button]["no"][seed] = frame

            add_seed(1, "mono", "lr", "a")
            add_seed(2, "mono", "la", "a")
            add_seed(3, "mono", "help", "a")
            add_seed(4, "stereo", "lr", "a")
            add_seed(5, "stereo", "la", "a")
            add_seed(6, "stereo", "help", "a")

    sheet_txt = requests.get(
        LG_JPN_SHEET,
        timeout=5,
    ).text
    sheet_csv = csv.reader(sheet_txt.split("\n"))
    for i, row in enumerate(sheet_csv):
        if i < 3:
            continue
        if row[0]:
            frame = int(row[0])

            def add_seed(col, sound, l, button):
                if row[col]:
                    seed = int(row[col], 16)
                    frlg_seeds["lg_jpn"][sound][l][button]["no"][seed] = frame
                    frlg_seeds["lg_jpn"][sound][l][button]["yes"][
                        (seed - 1) & 0xFFFF
                    ] = frame

            add_seed(1, "mono", "lr", "a")
            add_seed(2, "mono", "la", "a")
            add_seed(3, "mono", "help", "a")
            add_seed(4, "stereo", "lr", "a")
            add_seed(5, "stereo", "la", "a")
            add_seed(6, "stereo", "help", "a")

    for game, data in frlg_seeds.items():
        if game == "time_stamp":
            continue
        for _sound, data in data.items():
            for _l, data in data.items():
                for _button, data in data.items():
                    data["no"] = {
                        seed: (frame, i)
                        for i, (seed, frame) in enumerate(sorted(data["no"].items(), key=lambda x: x[1]))
                    }
                    data["yes"] = {
                        seed: (frame, i)
                        for i, (seed, frame) in enumerate(sorted(data["yes"].items(), key=lambda x: x[1]))
                    }

    with open(
        "./js_finder/js_finder/resources/generated/frlg_seeds.json",
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(frlg_seeds, f)


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


def build_rtc_seeds():
    """Build RTC seeds"""
    rtc_seeds = {}
    epoch = datetime(year=2000, month=1, day=1)
    date_time = epoch
    while date_time.year < 2001:
        date_time += timedelta(minutes=1)
        days = (date_time - epoch).days + 1
        v = (
            1440 * days
            + 960 * (date_time.hour // 10)
            + 60 * (date_time.hour % 10)
            + 16 * (date_time.minute // 10)
            + (date_time.minute % 10)
        )
        seed = (v >> 16) ^ (v & 0xFFFF)
        rtc_seeds.setdefault(seed, int((date_time - epoch).total_seconds()))

    rtc_data = np.empty((len(rtc_seeds), 3), np.uint32)
    for i, (seed, seconds) in enumerate(rtc_seeds.items()):
        # for every initial seed, compute the distance from initial seed -> base seed + the "frames" of rtc required to hit it
        dist = distance(seed, BASE_SEED)
        seed_time = seconds * 60
        rtc_data[i] = (dist + seed_time) & 0xFFFFFFFF, seed_time, seed
    # sort by "total time"
    rtc_data = rtc_data[rtc_data[:, 0].argsort()]

    np.save("./js_finder/js_finder/resources/generated/rtc_data.npy", rtc_data)


def build_ten_lines_precalc():
    """Build ten lines precalc"""
    data = np.empty((0x10000, 2), np.uint32)
    for seed in range(0x10000):
        # for every initial seed, compute the distance from initial seed -> base seed
        data[seed] = distance(seed, BASE_SEED), seed
    # sort by distance
    data = data[data[:, 0].argsort()]
    np.save("./js_finder/js_finder/resources/generated/ten_lines_precalc.npy", data)


if __name__ == "__main__":
    pull_frlg_seeds()
    build_ten_lines_precalc()
    build_rtc_seeds()
