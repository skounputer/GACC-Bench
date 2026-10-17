---
pretty_name: GACC-Bench
language:
  - en
  - zh
task_categories:
  - question-answering
  - text-generation
tags:
  - benchmark
  - context-compression
  - long-context
  - goal-conditioned
  - evaluation
  - arxiv:2610.21893
size_categories:
  - n<1K
configs:
  - config_name: default
    default: true
    data_files:
      - split: test
        path: data/default/test-00000-of-00001.parquet
  - config_name: testmini
    data_files:
      - split: test
        path: data/testmini/test-00000-of-00001.parquet
---

<div align="center">

# GACC-Bench

### Benchmarking Goal-Adaptive Context Compression Ability across Large Language Models

[Paper](https://arxiv.org/abs/2610.21893) | [Code](https://github.com/weiting24/GACC-Bench) | [Dataset](https://huggingface.co/datasets/{{DATASET_ID}})

</div>

## Overview

GACC-Bench evaluates whether a language model can retain information relevant to a specified goal under a context-length budget. The compressor sees a source context, a goal, and a token budget. A reader then answers the associated questions using the compressed context; those questions are withheld from the compressor.

This Hugging Face release preserves the goal-level records and nested questions from the [GitHub release](https://github.com/weiting24/GACC-Bench). Parquet files support `datasets.load_dataset` and the dataset viewer. Original JSONL files remain available under `original/` for the evaluator.

## Dataset statistics

| Configuration | Split | Contexts | Goals / rows | Questions |
| --- | --- | ---: | ---: | ---: |
| `default` | `test` | 281 | 500 | 2,571 |
| `testmini` | `test` | 62 | 124 | 651 |

`testmini` is an exact subset of the complete benchmark, with two goals per selected context. It is a convenience configuration for smaller evaluations, not a disjoint validation set. Both configurations are evaluation data.

| Source collection | Contexts | Goals | Questions |
| --- | ---: | ---: | ---: |
| HELMET | 27 | 40 | 208 |
| L-Eval (`LEval`) | 67 | 102 | 526 |
| LongBench-v2 | 23 | 49 | 246 |
| LongCodeBench | 35 | 78 | 391 |
| Loong | 44 | 102 | 573 |
| MeetingBank | 67 | 101 | 489 |
| SWE-agent | 18 | 28 | 138 |

## Load with datasets

```python
from datasets import load_dataset

dataset = load_dataset("{{DATASET_ID}}", split="test")
mini = load_dataset("{{DATASET_ID}}", name="testmini", split="test")

example = dataset[0]
print(example["dataset"], example["goal"])
print(example["questions"][0]["question"])
```

Each row contains one goal. The same source context can appear in multiple rows with different goals.

| Field | Type | Description |
| --- | --- | --- |
| `dataset` | string | Source collection identifier |
| `context_id` | string | Source context identifier |
| `context` | string | Full source context |
| `goal_id` | string | Unique goal identifier |
| `goal` | string | High-level information-retention goal |
| `questions` | list of objects | Questions associated with this goal |
| `questions[].question_id` | string | Question identifier |
| `questions[].question` | string | Evaluation question |
| `questions[].gold_answer` | string | Reference answer |

## Use with the evaluation code

```python
from huggingface_hub import hf_hub_download

path = hf_hub_download(
    repo_id="{{DATASET_ID}}",
    repo_type="dataset",
    filename="original/GACC-Bench.jsonl",
    local_dir="hf_data",
)
print(path)
```

Pass the downloaded file to `run.sh --input` in the [evaluation repository](https://github.com/weiting24/GACC-Bench). The default compression budgets are 5% and 10% of source-context tokens. Code, prompts, metrics, and command-line options are documented there.

## Provenance

`SOURCE.json` records the source commit, byte-level SHA-256 checksums of the original JSONL files, and checksums of the Parquet exports. The Parquet data retains the original row order, field values, and question order. Contexts originate from the seven source collections listed above; retain their original attribution when reusing those materials.

## Citation

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
