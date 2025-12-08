# run_download_and_save.py
import time
from tqdm import tqdm
from neo4j.exceptions import ServiceUnavailable

from download_data import fetch_batch, get_total_rows, close_driver
from save_data_to_csv import open_new_csv, write_batch_to_csv
from save_data_to_csv import OUT_DIR

BATCH_SIZE = 50000
RETRY_DELAY = 360

QUERY = """
    MATCH (e1)-[r]->(e2)
    WHERE apoc.rel.id(r) > $last_rid
    RETURN apoc.rel.id(r) AS rid,
           apoc.node.id(e1) AS entity_1,
           type(r) AS predicate,
           apoc.node.id(e2) AS entity_2,
           labels(e1)[0] AS label_e1,
           labels(e2)[0] AS label_e2
    ORDER BY rid
    LIMIT $batch
"""

def main():
    total_rows = get_total_rows()
    print("Starting to download data from Neo4j...")
    pbar = tqdm(total=total_rows, desc="Export rows", unit=" rows")

    last_rid = -1
    file_index = 1
    rows_in_file = 0

    f = None
    writer = None

    while True:
        try:
            records = fetch_batch(QUERY, last_rid, BATCH_SIZE)
            if not records:
                break

            if rows_in_file == 0:
                if f:
                    f.close()
                f, writer = open_new_csv(file_index)
                file_index += 1

            rows_in_file, last_rid, rotated = write_batch_to_csv(
                records, f, writer, rows_in_file, BATCH_SIZE
            )

            pbar.update(len(records))

            if rotated:
                rows_in_file = 0

        except ServiceUnavailable as e:
            print(f"[!] Lost connect: {e}. Wait for {RETRY_DELAY}...")
            time.sleep(RETRY_DELAY)

    if f:
        f.close()

    close_driver()
    pbar.close()
    print("Export finished")
    print(f"Data saved to {OUT_DIR}")

if __name__ == "__main__":
    main()
