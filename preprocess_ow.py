#!/bin/env python3
import json
import sys
import pathlib
import re
from collections import defaultdict

if len(sys.argv) < 2:
    print("./measure_owperf <directory>")
    print("you need to pass a directory containing owperf .txt files")
    exit()

for arg in sys.argv[1:]:
    print("extracting", arg)

    file = open(arg, "r")
    lines = file.read()

    data_string = re.split("MASTER-0:\s*?bi,\s*?as,\s*?ae,\s*?ts,\s*?ta,\s*?oea,\s*?oer,\s*?d,\s*?ad,\s*?ai,\s*?ora,\s*?rtt,\s*?ortt", lines)

    ow_data = defaultdict(lambda: [])
    for line in data_string[1].strip().split('\n'):
        process, values = line.split(':')

        parsed = {}
        values = [int(v) * 1000 if v.strip().isdecimal() else 0 for v in values.split(',')]
        parsed["bi"  ] = values[ 0]
        parsed["as"  ] = values[ 1]
        parsed["ae"  ] = values[ 2]
        # parsed["ts"]   = int(values[3])
        # parsed["ta"]   = int(values[4])
        parsed["oea" ] = values[ 5]
        parsed["oer" ] = values[ 6]
        parsed["d"   ] = values[ 7]
        parsed["ad"  ] = values[ 8]
        parsed["ai"  ] = values[ 9]
        parsed["ora" ] = values[10]
        parsed["rtt" ] = values[11]
        parsed["ortt"] = values[12]
        ow_data[process].append(parsed)

    clients = len(ow_data)
    iterations = len(list(ow_data.values())[0])

    data = []
    for value in ow_data.values():
        data.append({
            "invocation": {
                "start": [v["bi"] for v in value],
                "end"  : [v["ai"] for v in value],
            },
            "worker": {
                "start": [v["as"] for v in value],
                "end"  : [v["ae"] for v in value],
            },
            "runtime": {
                "start": [v["as"] for v in value],
                "end"  : [v["ae"] for v in value],
            },
            "function": {
                "start": [v["as"] + (v["ae"] - v["as"] - v["d"])/2 for v in value],
                "end"  : [v["ae"] - (v["ae"] - v["as"] - v["d"])/2 for v in value],
                "internal_duration": [v["d"] for v in value],
            },
        });

    with open(pathlib.Path(arg).with_suffix('.json'), "w", encoding="utf8") as json_file:
        json.dump(data, json_file, indent=2)  # , ensure_ascii = False)
