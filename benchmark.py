#!/bin/env python3
import json
import sys
import math
import os
import pandas as pd
import numpy as np

frames = []

# preprocesses values are passed as directory of .json files
# second argument specifies the output filename

if len(sys.argv) < 3:
    print(
        "You need to pass a directory of measured data and an output file name",
        file=sys.stderr,
    )
    exit(1)

directory = sys.argv[1]
directory_entries = [os.path.join(directory, file) for file in os.listdir(directory)]
directory_jsons = [
    file
    for file in directory_entries
    if os.path.isfile(file)
    and os.path.splitext(file)[1] == ".json"
    and "enriched" not in file
]

for json_file in directory_jsons:
    with open(json_file) as file:
        data_list = json.load(file)

    clients = len(data_list)

    collected_data = []
    for data in data_list:
        # data of a single client
        d = pd.DataFrame.from_dict(
            {(i, j): data[i][j] for i in data.keys() for j in data[i].keys()}
        )
        inconsistent = []
        for i in d.index:
            time_stamps = []
            if i != 0:
                time_stamps += [d["invocation", "end"][i - 1]]
            time_stamps += [
                d["invocation", "start"][i],
                d["worker", "start"][i],
                d["runtime", "start"][i],
                d["function", "start"][i],
                d["function", "end"][i],
                d["runtime", "end"][i],
                d["worker", "end"][i],
                d["invocation", "end"][i],
            ]
            if i != len(d) - 1:
                time_stamps += [d["invocation", "start"][i + 1]]
            if time_stamps != sorted(time_stamps):
                print("found inconsistency at index", i)
                inconsistent.append(i)
        collected_data.append(d.drop(inconsistent))
    df = pd.concat(collected_data, ignore_index=True)  # , keys=range(0,len(data_list)))

    # convert all entries to float64 -- int will fail on calculating mean
    # df = df.astype(np.float64)

    iterations = math.ceil(len(df.index) / clients)

    for index in set(i for i, j in df.columns):
        df[index, "delta"] = df[index, "end"] - df[index, "start"]
        # del df[index, "start"]
        # del df[index, "end"]

    df["communication", "send"] = df["worker", "start"] - df["invocation", "start"]
    df["worker", "creation"] = df["runtime", "start"] - df["worker", "start"]
    df["runtime", "creation"] = df["function", "start"] - df["runtime", "start"]
    # df["function"     , "duration"] = df[[["function", "delta"],["function", "internal_duration"]]].max(axis=1)
    df["runtime", "deletion"] = df["runtime", "end"] - df["function", "end"]
    df["worker", "deletion"] = df["worker", "end"] - df["runtime", "end"]
    df["communication", "receive"] = df["invocation", "end"] - df["worker", "end"]

    df["runtime", "overhead"] = df["runtime", "delta"] - df["function", "delta"]
    df["worker", "overhead"] = df["worker", "delta"] - df["runtime", "delta"]
    df["communication", "overhead"] = df["invocation", "delta"] - df["worker", "delta"]

    df = df.sort_index(axis=1)

    name, _ = os.path.splitext(json_file)

    df.to_json(f"{name}-enriched.json")
    df.mean().to_json(f"{name}-enriched-mean.json")

    data = {
        (clients, "mean"): df.mean(),
        (clients, "min"): df.min(),
        (clients, "max"): df.max(),
        (clients, "error-min"): df.mean() - df.min(),
        (clients, "error-max"): df.max() - df.mean(),
        (clients, "median"): df.median(),
        (clients, "upper-quartile"): df.quantile(0.75),
        (clients, "lower-quartile"): df.quantile(0.25),
        (clients, "upper-whisker"): df[df<=df.quantile(0.75)+1.5*(df.quantile(0.75) - df.quantile(0.25))].max(),
        (clients, "lower-whisker"): df[df>=df.quantile(0.25)-1.5*(df.quantile(0.75) - df.quantile(0.25))].min(),
    }

    dataframe = pd.DataFrame(data) / 1000

    dataframe = dataframe.stack()
    dataframe.index = ["-".join(col) for col in dataframe.index]

    frames.append(dataframe.transpose())

df = pd.concat(frames)

df.sort_index().to_csv(sys.argv[2], index_label="clients")
