#!/bin/env python3
import json
import sys
import pathlib

if len(sys.argv) < 2:
    print("you need to pass a filename")
    exit()

start_string = "====   OUTPUT   ===="
end_string = "==== END OUTPUT ===="

for arg in sys.argv[1:]:
    print("extracting", arg)

    file = open(arg, "r")
    line = file.read()

    data_string = line[line.find(start_string) + len(start_string):line.find(end_string)]
    data = json.loads(data_string)

    with open(pathlib.Path(arg).with_suffix('.json'), 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, indent=2)  # , ensure_ascii = False)
