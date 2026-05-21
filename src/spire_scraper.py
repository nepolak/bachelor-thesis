import argparse
from pathlib import Path
from requests.exceptions import HTTPError
import requests
import pandas as pd
from multiprocessing import Process, JoinableQueue, Queue
import time
import random


class TerminateClass():
    pass


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive integer." % value)
    return ivalue


def get_mags(sample_id: str):
    retries_count = 10

    for i in range(retries_count):
        try:
            with requests.get(f"https://spire.embl.de/spire/api/sample/{sample_id}?format=tsv", stream=True) as resp:
                if resp.status_code == 404:
                    return None

                resp.raise_for_status()

                df = pd.read_csv(resp.raw, delimiter="\t") #type: ignore

                return df if len(df) > 0 else None
        except HTTPError as err:
            if err.response is None:
                raise

            if err.response.status_code >= 500 or err.response.status_code == 429 or i == (retries_count - 1):
                time.sleep(random.uniform(1, 5))
                continue

            raise


def process_samples(queue: JoinableQueue, output: JoinableQueue):
    while True:
        sample_id: str | TerminateClass = queue.get()
        try:
            if isinstance(sample_id, TerminateClass):
                break

            mags = get_mags(sample_id)

            output.put(mags)
        except Exception as err:
            output.put(err)
            break
        finally:
            queue.task_done()


def consume_merge(input_queue: JoinableQueue, output_queue: JoinableQueue, ret_queue: Queue, total_items: int):
    all_dfs = []
    stuff_done = 0

    while True:
        mag_df: pd.DataFrame | Exception | TerminateClass = output_queue.get()
        if isinstance(mag_df, TerminateClass):
            break

        try:
            if isinstance(mag_df, Exception):
                input_queue.close()
                raise mag_df

            if mag_df is not None:
                all_dfs.append(mag_df)

            stuff_done += 1
            print(f"{stuff_done} out of {total_items}", flush=True)
        finally:
            output_queue.task_done()

    print("\n", flush=True)
    ret_df = pd.concat(all_dfs) if len(all_dfs) > 0 else pd.DataFrame()

    ret_queue.put(ret_df)


def scrape_multiproc(metadata: pd.DataFrame, concurrency: int):
    ret_queue = Queue(1)
    input_queue = JoinableQueue(concurrency)
    output_queue = JoinableQueue(concurrency)

    metadata_df = metadata.set_index("spire_sample_name")

    workers = [Process(target=process_samples, args=[input_queue, output_queue]) for a in range(concurrency)]
    consumer = Process(target=consume_merge, args=[input_queue, output_queue, ret_queue, len(metadata_df)])

    try:
        for process in workers + [consumer]:
            process.start()

        for sample_id in metadata_df.reset_index()["spire_sample_name"]:
            input_queue.put(sample_id, block=True)

        input_queue.join()
        output_queue.join()


        for _ in range(len(workers)):
            input_queue.put(TerminateClass())
        output_queue.put(TerminateClass())

        genome_df: pd.DataFrame = ret_queue.get(block=True)
        consumer.join()
        for worker in workers:
            worker.join()

        all_df = genome_df.set_index("sample_id").join(metadata_df, how="inner")

        return all_df
    finally:
        ret_queue.close()
        input_queue.close()
        output_queue.close()

        for worker in workers:
            worker.close()

        consumer.close()

    # if complete is not None:
    #     with open(complete, "wt+") as f:
    #         all_df.to_csv(f, index=True)
    
    # unique_df = all_df.groupby("sample_id").first().reset_index()
    # unique_df["spire_sample_name"] = unique_df["sample_id"]
    # unique_df["has_mag"] = ~unique_df["spire_id"].isna().astype(bool)
    # unique_df = unique_df[metadata_df.reset_index().columns.to_list() + ["has_mag"]]

    # return unique_df

    # with open(output, "wt+") as f:
    #     unique_df.to_csv(f, index=True)


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()

#     parser.add_argument("metadata")
#     parser.add_argument("output")
#     parser.add_argument("-c", help="Number of parallel requests to spire", default=16, type=check_positive, dest="concurrency")
#     parser.add_argument("-o", help="Complete file path", default=None, dest="complete")

#     args = parser.parse_args()

    

#     print("Done.")`



