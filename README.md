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

## Main Results

Results on **GACC-Bench-full** (500 goals, 2,571 questions) from [Table 2 of the paper](https://arxiv.org/html/2610.21893v1#S4.T2). The models below serve as compressors; **DeepSeek-V4-Pro** is the fixed reader and judge. Budgets specify the percentage of source-context tokens retained.

All scores are accuracy percentages (higher is better). The seven source columns report **Macro** accuracy; the last two columns report overall **Macro** and **Micro** accuracy. **Bold** marks the best score in each column within a budget, including ties.

### 5% retention budget

| Compressor | LBv2 | HELMET | L-Eval | Loong | MB | LCB | SWE | Overall Macro | Overall Micro |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6-Astra | **14.29** | **2.50** | 0.00 | **11.76** | 0.00 | **6.41** | **17.86** | **6.00** | 42.43 |
| GPT-6.1-Sol | **14.29** | **2.50** | **1.96** | 8.82 | 0.00 | **6.41** | 10.71 | 5.40 | **42.86** |
| GPT-5.6-Sol | 6.12 | **2.50** | **1.96** | 1.96 | 0.00 | 1.28 | 0.00 | 1.80 | 29.64 |
| Claude-Opus-5.5 | 6.12 | 0.00 | 0.00 | 6.86 | 0.00 | 3.85 | 3.57 | 2.80 | 28.94 |
| Gemini-3.6-flash | 2.04 | 0.00 | 0.00 | 0.00 | 0.00 | 1.28 | 0.00 | 0.40 | 20.30 |
| Qwen3.8-Max | 6.12 | **2.50** | **1.96** | 0.98 | 0.00 | **6.41** | 10.71 | 3.00 | 30.84 |
| GLM-5.3 | **14.29** | 0.00 | **1.96** | 7.84 | 0.00 | 5.13 | 10.71 | 4.80 | 31.19 |
| GLM-5.3-flash | 8.16 | 0.00 | 0.98 | 4.90 | 0.00 | 1.28 | 7.14 | 2.60 | 31.43 |
| DeepSeek-V4-Pro | 8.16 | **2.50** | 0.00 | 0.00 | 0.00 | 5.13 | 3.57 | 2.00 | 28.70 |
| Kimi-K3 | 10.20 | **2.50** | 0.98 | 2.94 | **0.99** | 3.85 | 7.14 | 3.20 | 28.67 |

### 10% retention budget

| Compressor | LBv2 | HELMET | L-Eval | Loong | MB | LCB | SWE | Overall Macro | Overall Micro |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6-Astra | **30.61** | 12.50 | **11.76** | 21.57 | 0.99 | **17.95** | 17.86 | **14.80** | **57.41** |
| GPT-6.1-Sol | **30.61** | 12.50 | 9.80 | **24.51** | 1.98 | 14.10 | **21.43** | **14.80** | 56.40 |
| GPT-5.6-Sol | 14.29 | 0.00 | 5.88 | 5.88 | 1.98 | 5.13 | 3.57 | 5.20 | 43.21 |
| Claude-Opus-5.5 | 20.41 | 7.50 | 1.96 | 14.71 | 1.98 | 11.54 | 17.86 | 9.20 | 43.95 |
| Gemini-3.6-flash | 18.37 | 2.50 | 0.00 | 1.96 | 0.00 | 5.13 | 7.14 | 3.60 | 33.68 |
| Qwen3.8-Max | 14.29 | **15.00** | 2.94 | 4.90 | 0.99 | 6.41 | 17.86 | 6.40 | 44.96 |
| GLM-5.3 | 20.41 | 7.50 | 7.84 | 15.69 | **2.97** | 12.82 | 14.29 | 10.80 | 48.46 |
| GLM-5.3-flash | 20.41 | **15.00** | 3.92 | 13.73 | **2.97** | 10.26 | 17.86 | 10.00 | 50.80 |
| DeepSeek-V4-Pro | 10.20 | 5.00 | 1.96 | 4.90 | 0.00 | **17.95** | 10.71 | 6.20 | 42.40 |
| Kimi-K3 | 20.41 | 5.00 | 2.94 | 5.88 | 1.98 | 6.41 | 17.86 | 6.60 | 45.62 |

**Metrics.** Macro is the percentage of goals for which every associated question is answered correctly. Micro is the percentage of individual questions answered correctly. Overall Macro is computed over all 500 goals, rather than by averaging the seven source scores.

**Abbreviations.** LBv2: LongBench-v2; MB: MeetingBank; LCB: LongCodeBench; SWE: agent trajectories from SWE-Bench Verified.

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
