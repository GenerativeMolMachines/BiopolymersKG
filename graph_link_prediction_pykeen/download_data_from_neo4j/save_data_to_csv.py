import csv
from pathlib import Path

OUT_DIR = Path("data/raw_data/export_iw")
OUT_DIR.mkdir(exist_ok=True, parents=True)

HEADER = ["rid", "entity_1", "predicate", "entity_2",
          "label_e1", "label_e2"]

def open_new_csv(file_index: int):
    path = OUT_DIR / f"export_part_{file_index:03d}.csv"
    f = open(path, "w", encoding="utf-8", newline="")
    writer = csv.writer(f)
    writer.writerow(HEADER)
    return f, writer

def write_batch_to_csv(records, file_handle, writer, rows_written, batch_limit):
    last_rid = None

    for rec in records:
        writer.writerow([
            rec["rid"],
            rec["entity_1"],
            rec["predicate"],
            rec["entity_2"],
            rec["label_e1"],
            rec["label_e2"]
        ])
        rows_written += 1
        last_rid = rec["rid"]

        if rows_written == batch_limit:
            file_handle.close()
            return rows_written, last_rid, True

    return rows_written, last_rid, False