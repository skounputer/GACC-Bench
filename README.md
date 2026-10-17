<div align="center">

# GACC-Bench: Benchmarking Goal-Adaptive Context Compression Ability across Large Language Models

<a href="https://arxiv.org/abs/2610.21893"><img src="https://img.shields.io/badge/Paper-arXiv%202610.21893-b31b1b" alt="Paper"></a>
<a href="https://huggingface.co/datasets/Regimes/GACC-Bench"><img src="https://img.shields.io/badge/Dataset-%F0%9F%A4%97%20Hugging%20Face-yellow" alt="Dataset"></a>
<a href="https://github.com/weiting24/GACC-Bench"><img src="https://img.shields.io/badge/Code-GitHub-black?logo=github" alt="Code"></a>

</div>

## Overview

**GACC-Bench** evaluates goal-adaptive context compression: how well a language model preserves information needed for a high-level goal under a token budget, before the downstream questions are known.

1. The **compressor** receives the full context, a goal, and a token budget.
2. A fixed **reader** answers the goal's questions individually using the compressed context.
3. A **judge** scores the answers against their references.

The benchmark contains **500 goals and 2,571 questions over 281 contexts**, spanning seven document and agent-trace collections. Evaluation questions are withheld from the compressor.

## News

- **[2026.10.17]** The dataset is available on [Hugging Face](https://huggingface.co/datasets/Regimes/GACC-Bench), with `load_dataset()` support, Parquet files, and original JSONL downloads.
- **[2026.10.15]** Our [paper](https://arxiv.org/abs/2610.21893) is available on arXiv.

## Dataset

| Configuration | Contexts | Goals | Questions |
| --- | ---: | ---: | ---: |
| Full benchmark (`default`) | 281 | 500 | 2,571 |
| Small evaluation subset (`testmini`) | 62 | 124 | 651 |

`testmini` contains two goals for each selected context and is a subset of the full benchmark. Both configurations use the `test` split.

### Load from Hugging Face

```bash
pip install datasets
```

```python
from datasets import load_dataset

dataset = load_dataset("Regimes/GACC-Bench", split="test")
mini = load_dataset("Regimes/GACC-Bench", name="testmini", split="test")

example = dataset[0]
print(example["goal"])
print(example["questions"][0]["question"])
```

Each row contains one goal, its full source context, and a list of questions with reference answers. The seven sources are HELMET, L-Eval, LongBench-v2, LongCodeBench, Loong, MeetingBank, and SWE-agent. Field descriptions and source-level statistics are in the [dataset card](https://huggingface.co/datasets/Regimes/GACC-Bench).

### Original JSONL files

The evaluator accepts the original files included in this repository:

- [`data/GACC-Bench.jsonl`](data/GACC-Bench.jsonl)
- [`data/GACC-Bench-testmini.jsonl`](data/GACC-Bench-testmini.jsonl)

The same files are hosted on Hugging Face under `original/`:

```python
from huggingface_hub import hf_hub_download

path = hf_hub_download(
    repo_id="Regimes/GACC-Bench",
    repo_type="dataset",
    filename="original/GACC-Bench.jsonl",
    local_dir="hf_data",
)
```

Use the returned `path` as the evaluator's `--input` when downloading from Hugging Face.

## Installation

```bash
git clone https://github.com/weiting24/GACC-Bench.git
cd GACC-Bench
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The compressor, reader, and judge are configured independently using OpenAI-compatible APIs.

## Evaluation

Replace the endpoint, key, and model placeholders with your own API settings:

```bash
bash run.sh \
  --input ./data/GACC-Bench.jsonl \
  --output ./runs/gacc_eval \
  --limit 0 \
  --budgets 5,10 \
  --include-full-context true \
  --compressor-url '<COMPRESSOR_URL>' \
  --compressor-key '<COMPRESSOR_KEY>' \
  --compressor-model '<COMPRESSOR_MODEL>' \
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

Use `--limit 10` and a separate output directory for a smaller run. Budgets are percentages of the original context length; `5,10` evaluates 5% and 10% conditions. The full-context option adds the uncompressed reference condition.

| Metric | Definition |
| --- | --- |
| Micro accuracy | Fraction of questions answered correctly |
| Macro accuracy | Fraction of goals for which every associated question is answered correctly |

The evaluator writes `reports/metrics.json`, `reports/results.jsonl`, and reusable artifacts under `memories/`, `answers/`, and `judgments/`. Detailed output fields, retry behavior, and budget accounting are documented in the [evaluation guide](docs/EVALUATION.md).

## Dataset export

To reproduce the Hugging Face files from the checked-in JSONL:

```bash
pip install pyarrow
python scripts/export_huggingface.py --output ./release/huggingface
```

The exporter checks lossless Parquet round trips and subset membership, copies the original files byte-for-byte, and records source checksums in `SOURCE.json`. The [dataset card template](docs/huggingface-dataset-card.md) contains the split/configuration metadata.

## Citation

If you use GACC-Bench, please cite:

```bibtex
@misc{liu2026gaccbench,
  title={GACC-Bench: Benchmarking Goal-Adaptive Context Compression Ability across Large Language Models},
  author={Weiting Liu and Zhiyu Pan and Shuhong Wang and Zhenquan Yao and Jungang Li and Li Zhao and Jian Jiang and Jianfeng Feng and Ai Han and Wenlian Lu},
  year={2026},
  eprint={2610.21893},
  archivePrefix={arXiv},
  primaryClass={cs.IR},
  url={https://arxiv.org/abs/2610.21893}
}
```
