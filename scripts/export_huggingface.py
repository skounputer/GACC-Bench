#!/usr/bin/env python3
"""Export the benchmark to a viewer-friendly Hugging Face dataset directory.

Requires: pip install pyarrow
Original JSONL files are retained byte-for-byte; Parquet preserves their nested
question lists and goal-level row granularity.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import pyarrow as pa
    import pyarrow.parquet as pq

    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repo-id", default="Regimes/GACC-Bench")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    schema = pa.schema(
        [
            ("dataset", pa.string()),
            ("context_id", pa.string()),
            ("context", pa.string()),
            ("goal_id", pa.string()),
            ("goal", pa.string()),
            (
                "questions",
                pa.list_(
                    pa.struct(
                        [
                            ("question_id", pa.string()),
                            ("question", pa.string()),
                            ("gold_answer", pa.string()),
                        ]
                    )
                ),
            ),
        ]
    )
    manifest = {
        "source_repository": "https://github.com/weiting24/GACC-Bench",
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
        ).strip(),
        "files": [],
    }
    source_rows = {}
    for config, filename in [
        ("default", "GACC-Bench.jsonl"),
        ("testmini", "GACC-Bench-testmini.jsonl"),
    ]:
        source = root / "data" / filename
        # JSONL records are separated by newline bytes. Unicode line separators
        # can occur inside valid context strings, so do not use str.splitlines.
        with source.open(encoding="utf-8") as stream:
            rows = [json.loads(line) for line in stream if line.strip()]
        if len({row["goal_id"] for row in rows}) != len(rows):
            raise ValueError(f"Duplicate goal IDs in {filename}")
        table = pa.Table.from_pylist(rows, schema=schema)
        parquet = args.output / "data" / config / "test-00000-of-00001.parquet"
        parquet.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, parquet, compression="zstd")
        if pq.read_table(parquet).to_pylist() != rows:
            raise ValueError(f"Parquet round-trip changed rows from {filename}")
        original = args.output / "original" / filename
        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, original)
        assert sha256(original) == sha256(source)
        record = {
            "config": config,
            "split": "test",
            "goals": len(rows),
            "contexts": len({(row["dataset"], row["context_id"]) for row in rows}),
            "questions": sum(len(row["questions"]) for row in rows),
            "original_path": str(original.relative_to(args.output)),
            "original_sha256": sha256(original),
            "parquet_path": str(parquet.relative_to(args.output)),
            "parquet_sha256": sha256(parquet),
        }
        manifest["files"].append(record)
        source_rows[config] = rows
        print(json.dumps(record, ensure_ascii=False))
    index = {row["goal_id"]: row for row in source_rows["default"]}
    if not all(index.get(row["goal_id"]) == row for row in source_rows["testmini"]):
        raise ValueError("testmini must be an exact subset of the complete benchmark")
    card = (root / "docs/huggingface-dataset-card.md").read_text(encoding="utf-8")
    (args.output / "README.md").write_text(
        card.replace("{{DATASET_ID}}", args.repo_id), encoding="utf-8"
    )
    (args.output / "SOURCE.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
