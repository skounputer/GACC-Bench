# GACC-Bench Evaluation

Paper: [GACC-Bench: Benchmarking Goal-Adaptive Context Compression Ability across Large Language Models](https://arxiv.org/abs/2610.21893)

This directory evaluates one JSONL file with the GACC-Bench protocol. The
compressor, reader, and judge are configured independently through
OpenAI-compatible APIs. Budgets are specified as percentages of the original
source-context length; the default is 5% and 10%.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Data

- `data/GACC-Bench.jsonl`: the complete GACC-Bench release with 500 goals.
- `data/GACC-Bench-testmini.jsonl`: a controlled two-goal subset extracted from
  `GACC-Bench.jsonl`, containing 62 contexts, 124 goals, and 651 questions.

## Run

Use `--limit 10` for a smoke test or `--limit 0` for all input goals. Use
`--budgets 5,10` for the default conditions, or pass any comma-separated
percentages such as `--budgets 1,2,5,10,20`. Set
`--include-full-context true` to include the uncompressed reference condition.

```bash
./run.sh \
  --input ./data/GACC-Bench.jsonl \
  --output ./runs/gacc_eval \
  --limit 0 \
  --include-full-context true \
  --compressor-url '<COMPRESSOR_URL>' \
  --compressor-key '<COMPRESSOR_KEY>' \
  --compressor-model '<COMPRESSOR_MODEL>' \
  --budgets 5,10 \
  --reader-url '<READER_URL>' \
  --reader-key '<READER_KEY>' \
  --reader-model '<READER_MODEL>' \
  --judge-url '<JUDGE_URL>' \
  --judge-key '<JUDGE_KEY>' \
  --judge-model '<JUDGE_MODEL>' \
  --workers 300 \
  --max-attempts 30 \
  --retry-sleep 30
```

Replace `--limit 0` with `--limit 10` and choose a different output directory for a smoke test. For each source context, the evaluator computes `floor(source_tokens * budget_ratio)` and provides that token limit to the compressor. Successful memories, answers, and judgments for the same model are reused on later runs; failed, missing, or model-mismatched artifacts are retried. Requests retry up to 30 times with a 30-second delay between attempts.

## Output

```text
runs/gacc_eval/
├── reports/metrics.json
├── reports/results.jsonl
├── memories/
├── answers/
└── judgments/
```

`metrics.json` contains per-benchmark and overall Micro/Macro accuracy.
`results.jsonl` is aligned with the input JSONL and records question-level
judgments, goal-level results, validity/failure status, and per-budget token
usage. The terminal summary also reports aggregate budget usage.
