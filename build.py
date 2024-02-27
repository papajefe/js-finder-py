"""Additional setup to be run by build.sh"""

from datetime import datetime
import csv
import json
import requests


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

    with open(
        "./js_finder/js_finder/resources/generated/frlg_seeds.json",
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(frlg_seeds, f)


if __name__ == "__main__":
    pull_frlg_seeds()
