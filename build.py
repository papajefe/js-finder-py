"""Additional setup to be run by build.sh"""

from datetime import datetime
import csv
import json
import requests


def pull_frlg_seeds():
    """Pull FRLG seed from spreadsheet"""
    time_stamp = datetime.now()

    sheet_txt = requests.get(
        "https://docs.google.com/spreadsheets/d/1Mf3F4kTvNEYyDGWKVmMSiar3Fwh1PLzWVXUvGx9YxfA/gviz/tq?tqx=out:csv&sheet=Fire%20Red%20Raw%20Seed%20Data",
        timeout=5,
    ).text
    sheet_csv = csv.reader(sheet_txt.split("\n"))
    frlg_seeds = {"time_stamp": str(time_stamp)}
    for i, row in enumerate(sheet_csv):
        if i == 0:
            continue
        if row[0] and row[3] and row[3] != "-":
            # TODO: other sheets + other settings
            program_frame_str, _, _, seed_hex, *_ = row
            program_frame = int(program_frame_str)
            seed = int(seed_hex, 16)
            if seed >= 0x10000:
                continue
            # TODO: for now only store the earliest example of a given seed
            if seed not in frlg_seeds:
                frlg_seeds[seed] = program_frame
    with open(
        "./js_finder/js_finder/resources/generated/frlg_seeds.json",
        "w+",
        encoding="utf-8",
    ) as f:
        json.dump(frlg_seeds, f)


if __name__ == "__main__":
    pull_frlg_seeds()
