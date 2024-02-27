"""Additional setup to be run by build.sh"""

from datetime import datetime
import csv
import json
import requests


FR_ENG_SHEET = "https://docs.google.com/spreadsheets/d/1Mf3F4kTvNEYyDGWKVmMSiar3Fwh1PLzWVXUvGx9YxfA/gviz/tq?tqx=out:csv&sheet=Fire%20Red%20Raw%20Seed%20Data"


def pull_frlg_seeds():
    """Pull FRLG seed from spreadsheet"""
    time_stamp = datetime.now()
    frlg_seeds = {
        "time_stamp": str(time_stamp),
    } | {
        sound: {
            l: {
                button: {select: {} for select in ("yes", "no")}
                for button in ("a", "start") + (("l",) if l == "la" else ())
            }
            for l in ("la", "help", "lr")
        }
        for sound in ("stereo", "mono")
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
                        frlg_seeds[sound][l][button]["no"][seed] = frlg_seeds[sound][l][
                            button
                        ]["yes"][(seed + (7 if l == "help" else -1)) & 0xFFFF] = (
                            program_frame / 2
                        )

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

    with open(
        "./js_finder/js_finder/resources/generated/frlg_seeds.json",
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(frlg_seeds, f)


if __name__ == "__main__":
    pull_frlg_seeds()
