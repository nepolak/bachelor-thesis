from gzip import GzipFile
from pathlib import Path
import random
from typing import Iterable
import pandas as pd
import requests
import argparse
from multiprocessing import Pool
from os.path import join
from os import makedirs
from shutil import copyfileobj
from requests.exceptions import HTTPError
import time


def _fetch_mag_ids(sample_id: str):
    with requests.get(f"https://spire.embl.de/api/sample/{sample_id}?format=tsv", stream=True) as response:
        return list(pd.read_csv(filepath_or_buffer=response.raw, delimiter='\t')["spire_id"]) # type: ignore[arg-type]


def _fetch_mag(mag_id: str, dest_name: str):
    retries_count = 10
    for i in range(retries_count):
        try:
            with requests.get(f"https://spire.embl.de/download_file/{mag_id}", stream=True) as response:
                response.raise_for_status()

                with GzipFile(fileobj=response.raw) as gzip, open(dest_name, "wb") as output_file:
                    copyfileobj(gzip, output_file)
                    return
                
        except HTTPError as err:
            if err.response is None:
                raise

            if err.response.status_code == 500 or err.response.status_code == 429 or i == (retries_count - 1):
                time.sleep(random.uniform(1, 5))
                continue

            raise



def fetch_mags(spire_ids: pd.Series[str], output_path: Path, concurrency: int):
    with Pool(concurrency) as pool:
        makedirs(output_path, exist_ok=True)
        pool.starmap(_fetch_mag, ((spire_id, output_path / f"{spire_id}.fa") for spire_id in spire_ids))


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()

#     parser.add_argument("source", choices=["sample", "mag"])
#     parser.add_argument("input_csv")
#     parser.add_argument("-o", dest="output", default="downloaded_mags")
#     parser.add_argument("-c", type=int, dest="concurrency", default=32)

#     args = parser.parse_args()

#     if args.source == "sample":
#         with Pool(args.concurrency) as pool:
#             samples = list(pd.read_csv(args.input_csv)["spire_sample_name"])

#             jobs = list(zip(pool.map(_fetch_mag_ids, samples), samples))

#             makedirs(join(args.output), exist_ok=True)

#             feed = [(mag_id, join(args.output, f"{mag_tuple[1]}_{mag_id}.fa"), mag_tuple[1]) for mag_tuple in jobs for mag_id in mag_tuple[0]]

#             pool.starmap(_fetch_mag, (a[0:2] for a in feed))

#             print(f"Downloaded {len(feed)} mags.")

#             index_df = pd.DataFrame(
#                 { 
#                     "mag_id": [a[0] for a in feed],
#                     "sample_id": [a[2] for a in feed],
#                     "file_name": [a[1] for a in feed],
#                 })
#             index_df.to_csv(join(args.output, "index.csv"), index=False)
#     elif args.source == "mag":
#         with Pool(args.concurrency) as pool:
#             mags = pd.read_csv(args.input_csv)[["sample_id", "spire_id"]]
#             mags["filename"] = mags.apply(lambda x: join(args.output, f"{x['sample_id']}_{x['spire_id']}.fa"), axis=1)

#             makedirs(join(args.output), exist_ok=True)
#             pool.starmap(_fetch_mag, (a[1].tolist()[1:] for a in mags.iterrows()))

#             print(f"Downloaded {len(mags)} mags.")

#             mags.to_csv(join(args.output, "index.csv"), index=False)

