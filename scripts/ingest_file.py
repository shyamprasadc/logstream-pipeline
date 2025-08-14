from __future__ import annotations

import argparse
from app.ingestion.file_reader import read_lines
from app.parsing.parser import parse_line
from app.transformation.transformer import transform
from app.storage.postgres import init_db, insert_records
from app.storage.s3 import write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    init_db()
    batch = []
    for line in read_lines(args.file):
        p = parse_line(line)
        if not p:
            continue
        batch.append(transform(p))

    if batch:
        insert_records(batch)
        try:
            write_jsonl(batch)
        except Exception:
            pass


if __name__ == "__main__":
    main()
