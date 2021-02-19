from collections import defaultdict
from pathlib import Path
import pickle
import pandas as pd


def read_cache(cache):
    if cache.is_file():
        with cache.open("rb") as fobj:
            return pickle.load(fobj)
    

if __name__ == "__main__":
    data_cache = Path.cwd() / f"cache-1900-2020-20200101-20210101.pickle"
    data = read_cache(data_cache)

    rows = []
    for year, yeardata in data["years"].items():
        for person, persondata in yeardata.items():
            rows.append([person, year, persondata["views"]])
    
    dataframe = pd.DataFrame.from_records(rows, columns=["person", "year", "views"], index="person")
    dataframe.to_csv("data.csv")