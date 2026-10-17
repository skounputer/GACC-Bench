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

Scroll horizontally to view all columns.

### 5% retention budget

<table>
  <thead>
    <tr>
      <th nowrap>Compressor</th>
      <th nowrap>LongBench-v2</th>
      <th nowrap>HELMET</th>
      <th nowrap>L-Eval</th>
      <th nowrap>Loong</th>
      <th nowrap>MeetingBank</th>
      <th nowrap>LongCodeBench</th>
      <th nowrap>SWE-agent (SWE-Bench Verified)</th>
      <th nowrap>Overall Macro</th>
      <th nowrap>Overall Micro</th>
    </tr>
  </thead>
  <tbody>
    <tr><td nowrap>GPT-6-Astra</td><td align="right"><strong>14.29</strong></td><td align="right"><strong>2.50</strong></td><td align="right">0.00</td><td align="right"><strong>11.76</strong></td><td align="right">0.00</td><td align="right"><strong>6.41</strong></td><td align="right"><strong>17.86</strong></td><td align="right"><strong>6.00</strong></td><td align="right">42.43</td></tr>
    <tr><td nowrap>GPT-6.1-Sol</td><td align="right"><strong>14.29</strong></td><td align="right"><strong>2.50</strong></td><td align="right"><strong>1.96</strong></td><td align="right">8.82</td><td align="right">0.00</td><td align="right"><strong>6.41</strong></td><td align="right">10.71</td><td align="right">5.40</td><td align="right"><strong>42.86</strong></td></tr>
    <tr><td nowrap>GPT-5.6-Sol</td><td align="right">6.12</td><td align="right"><strong>2.50</strong></td><td align="right"><strong>1.96</strong></td><td align="right">1.96</td><td align="right">0.00</td><td align="right">1.28</td><td align="right">0.00</td><td align="right">1.80</td><td align="right">29.64</td></tr>
    <tr><td nowrap>Claude-Opus-5.5</td><td align="right">6.12</td><td align="right">0.00</td><td align="right">0.00</td><td align="right">6.86</td><td align="right">0.00</td><td align="right">3.85</td><td align="right">3.57</td><td align="right">2.80</td><td align="right">28.94</td></tr>
    <tr><td nowrap>Gemini-3.6-flash</td><td align="right">2.04</td><td align="right">0.00</td><td align="right">0.00</td><td align="right">0.00</td><td align="right">0.00</td><td align="right">1.28</td><td align="right">0.00</td><td align="right">0.40</td><td align="right">20.30</td></tr>
    <tr><td nowrap>Qwen3.8-Max</td><td align="right">6.12</td><td align="right"><strong>2.50</strong></td><td align="right"><strong>1.96</strong></td><td align="right">0.98</td><td align="right">0.00</td><td align="right"><strong>6.41</strong></td><td align="right">10.71</td><td align="right">3.00</td><td align="right">30.84</td></tr>
    <tr><td nowrap>GLM-5.3</td><td align="right"><strong>14.29</strong></td><td align="right">0.00</td><td align="right"><strong>1.96</strong></td><td align="right">7.84</td><td align="right">0.00</td><td align="right">5.13</td><td align="right">10.71</td><td align="right">4.80</td><td align="right">31.19</td></tr>
    <tr><td nowrap>GLM-5.3-flash</td><td align="right">8.16</td><td align="right">0.00</td><td align="right">0.98</td><td align="right">4.90</td><td align="right">0.00</td><td align="right">1.28</td><td align="right">7.14</td><td align="right">2.60</td><td align="right">31.43</td></tr>
    <tr><td nowrap>DeepSeek-V4-Pro</td><td align="right">8.16</td><td align="right"><strong>2.50</strong></td><td align="right">0.00</td><td align="right">0.00</td><td align="right">0.00</td><td align="right">5.13</td><td align="right">3.57</td><td align="right">2.00</td><td align="right">28.70</td></tr>
    <tr><td nowrap>Kimi-K3</td><td align="right">10.20</td><td align="right"><strong>2.50</strong></td><td align="right">0.98</td><td align="right">2.94</td><td align="right"><strong>0.99</strong></td><td align="right">3.85</td><td align="right">7.14</td><td align="right">3.20</td><td align="right">28.67</td></tr>
  </tbody>
</table>

### 10% retention budget

<table>
  <thead>
    <tr>
      <th nowrap>Compressor</th>
      <th nowrap>LongBench-v2</th>
      <th nowrap>HELMET</th>
      <th nowrap>L-Eval</th>
      <th nowrap>Loong</th>
      <th nowrap>MeetingBank</th>
      <th nowrap>LongCodeBench</th>
      <th nowrap>SWE-agent (SWE-Bench Verified)</th>
      <th nowrap>Overall Macro</th>
      <th nowrap>Overall Micro</th>
    </tr>
  </thead>
  <tbody>
    <tr><td nowrap>GPT-6-Astra</td><td align="right"><strong>30.61</strong></td><td align="right">12.50</td><td align="right"><strong>11.76</strong></td><td align="right">21.57</td><td align="right">0.99</td><td align="right"><strong>17.95</strong></td><td align="right">17.86</td><td align="right"><strong>14.80</strong></td><td align="right"><strong>57.41</strong></td></tr>
    <tr><td nowrap>GPT-6.1-Sol</td><td align="right"><strong>30.61</strong></td><td align="right">12.50</td><td align="right">9.80</td><td align="right"><strong>24.51</strong></td><td align="right">1.98</td><td align="right">14.10</td><td align="right"><strong>21.43</strong></td><td align="right"><strong>14.80</strong></td><td align="right">56.40</td></tr>
    <tr><td nowrap>GPT-5.6-Sol</td><td align="right">14.29</td><td align="right">0.00</td><td align="right">5.88</td><td align="right">5.88</td><td align="right">1.98</td><td align="right">5.13</td><td align="right">3.57</td><td align="right">5.20</td><td align="right">43.21</td></tr>
    <tr><td nowrap>Claude-Opus-5.5</td><td align="right">20.41</td><td align="right">7.50</td><td align="right">1.96</td><td align="right">14.71</td><td align="right">1.98</td><td align="right">11.54</td><td align="right">17.86</td><td align="right">9.20</td><td align="right">43.95</td></tr>
    <tr><td nowrap>Gemini-3.6-flash</td><td align="right">18.37</td><td align="right">2.50</td><td align="right">0.00</td><td align="right">1.96</td><td align="right">0.00</td><td align="right">5.13</td><td align="right">7.14</td><td align="right">3.60</td><td align="right">33.68</td></tr>
    <tr><td nowrap>Qwen3.8-Max</td><td align="right">14.29</td><td align="right"><strong>15.00</strong></td><td align="right">2.94</td><td align="right">4.90</td><td align="right">0.99</td><td align="right">6.41</td><td align="right">17.86</td><td align="right">6.40</td><td align="right">44.96</td></tr>
    <tr><td nowrap>GLM-5.3</td><td align="right">20.41</td><td align="right">7.50</td><td align="right">7.84</td><td align="right">15.69</td><td align="right"><strong>2.97</strong></td><td align="right">12.82</td><td align="right">14.29</td><td align="right">10.80</td><td align="right">48.46</td></tr>
    <tr><td nowrap>GLM-5.3-flash</td><td align="right">20.41</td><td align="right"><strong>15.00</strong></td><td align="right">3.92</td><td align="right">13.73</td><td align="right"><strong>2.97</strong></td><td align="right">10.26</td><td align="right">17.86</td><td align="right">10.00</td><td align="right">50.80</td></tr>
    <tr><td nowrap>DeepSeek-V4-Pro</td><td align="right">10.20</td><td align="right">5.00</td><td align="right">1.96</td><td align="right">4.90</td><td align="right">0.00</td><td align="right"><strong>17.95</strong></td><td align="right">10.71</td><td align="right">6.20</td><td align="right">42.40</td></tr>
    <tr><td nowrap>Kimi-K3</td><td align="right">20.41</td><td align="right">5.00</td><td align="right">2.94</td><td align="right">5.88</td><td align="right">1.98</td><td align="right">6.41</td><td align="right">17.86</td><td align="right">6.60</td><td align="right">45.62</td></tr>
  </tbody>
</table>

**Metrics.** Macro is the percentage of goals for which every associated question is answered correctly. Micro is the percentage of individual questions answered correctly. Overall Macro is computed over all 500 goals, rather than by averaging the seven source scores.

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
