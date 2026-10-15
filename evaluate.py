#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib import request

ROOT = Path(__file__).resolve().parent
RATIOS = (0.05, 0.10)
DATASETS = ("LBv2", "HELMET", "L-Eval", "Loong", "MB", "LCB", "SWE")
ALIASES = {"LongBench-v2": "LBv2", "HELMET": "HELMET", "LEval": "L-Eval",
           "Loong": "Loong", "MeetingBank": "MB", "LongCodeBench": "LCB",
           "SWE-agent": "SWE"}
ENCODER = None


def stamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def uid(*parts):
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:24]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    temp.replace(path)


def encoder():
    global ENCODER
    if ENCODER is None:
        import tiktoken
        ENCODER = tiktoken.get_encoding("cl100k_base")
    return ENCODER


def tokens(text):
    return len(encoder().encode(text or ""))


def prefix(text, limit):
    enc = encoder()
    return enc.decode(enc.encode(text)[:limit], errors="ignore")


def dataset(name):
    if name not in ALIASES:
        raise ValueError(f"unsupported dataset: {name}")
    return ALIASES[name]


def load(path, limit=None):
    bundles, goals, questions = [], set(), set()
    with path.open(encoding="utf-8", newline="") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_no}: {exc}") from exc
            for key in ("context_id", "goal_id", "context", "goal", "questions"):
                if key not in item:
                    raise ValueError(f"line {line_no} missing {key}")
            dataset(item.get("dataset", ""))
            if item["goal_id"] in goals or not item["questions"]:
                raise ValueError(f"invalid or duplicate goal at line {line_no}")
            goals.add(item["goal_id"])
            for question in item["questions"]:
                if not all(k in question for k in ("question_id", "question")):
                    raise ValueError(f"malformed question at line {line_no}")
                if "gold_answer" not in question and "original_gold_answer" not in question:
                    raise ValueError(f"question has no gold answer at line {line_no}")
                if question["question_id"] in questions:
                    raise ValueError(f"duplicate question: {question['question_id']}")
                questions.add(question["question_id"])
            bundles.append(item)
            if limit and len(bundles) >= limit:
                break
    if not bundles:
        raise ValueError("input JSONL is empty")
    return bundles


class Client:
    def __init__(self, base, key, qps, attempts, retry_sleep):
        self.url = base.rstrip("/") + "/chat/completions"
        self.key, self.interval = key, 1 / qps if qps > 0 else 0
        self.attempts, self.retry_sleep = attempts, retry_sleep
        self.lock, self.next_request = threading.Lock(), 0.0

    def _slot(self):
        with self.lock:
            now = time.monotonic()
            wait = max(0.0, self.next_request - now)
            self.next_request = max(now, self.next_request) + self.interval
        if wait:
            time.sleep(wait)

    def chat(self, model, prompt):
        body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"}
        error = "unknown error"
        for attempt in range(self.attempts):
            try:
                self._slot()
                req = request.Request(self.url, data=json.dumps(body, ensure_ascii=False).encode(),
                                      headers=headers, method="POST")
                with request.urlopen(req, timeout=600) as response:
                    value = json.loads(response.read().decode())
                text = value["choices"][0]["message"].get("content", "")
                if not isinstance(text, str) or not text.strip():
                    raise RuntimeError("empty model response")
                return text.strip()
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                if attempt + 1 < self.attempts:
                    time.sleep(self.retry_sleep)
        raise RuntimeError(f"failed after {self.attempts} attempts: {error}")


def template(name):
    return (ROOT / "prompts" / name).read_text(encoding="utf-8")


def fill(text, **values):
    replacements = {"{" + key + "}": str(value) for key, value in values.items()}
    if not replacements:
        return text
    pattern = re.compile("|".join(re.escape(key) for key in replacements))
    return pattern.sub(lambda match: replacements[match.group(0)], text)


def safe(text):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)


def boolean(value):
    value = value.lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def parse_budgets(value):
    try:
        budgets = [int(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("budgets must be comma-separated percentages") from exc
    if not budgets or any(budget <= 0 or budget > 100 for budget in budgets):
        raise argparse.ArgumentTypeError("budgets must be percentages in the range 1-100")
    if len(set(budgets)) != len(budgets):
        raise argparse.ArgumentTypeError("budgets must not contain duplicates")
    return tuple(budget / 100 for budget in budgets)


def percent(ratio):
    return int(round(ratio * 100))


def failure(kind, meta, exc):
    return {**meta, "status": "failed", "kind": kind, "error": str(exc), "finished_at": stamp()}


def reusable(path, model):
    if not path.exists():
        return False
    try:
        value = read(path)
        return value.get("status") == "ok" and value.get("model") == model
    except Exception:
        return False


def memory_path(root, ratio, bundle):
    return root / "memories" / f"{percent(ratio)}%" / f"{uid('memory', bundle['context_id'], bundle['goal_id'], ratio)}.json"


def answer_path(root, condition, ratio, qid):
    return root / "answers" / safe(condition) / f"{uid('answer', condition, ratio, qid)}.json"


def judgment_path(root, condition, qid):
    return root / "judgments" / safe(condition) / f"{uid('judge', condition, qid)}.json"


def compress(client, model, bundle, ratio, root):
    path = memory_path(root, ratio, bundle)
    if reusable(path, model):
        return path
    source_tokens = tokens(bundle["context"])
    budget = max(1, math.floor(source_tokens * ratio))
    prompt = fill(template("compression.txt"), limit=str(budget), goal=bundle["goal"], context=bundle["context"])
    meta = {"type": "memory", "model": model, "context_id": bundle["context_id"],
            "goal_id": bundle["goal_id"], "ratio": ratio}
    try:
        raw = client.chat(model, prompt)
        memory = prefix(raw, budget)
        if not memory:
            raise RuntimeError("empty memory after token control")
        value = {**meta, "status": "ok", "memory": memory, "source_tokens": source_tokens,
                 "budget_tokens": budget, "generated_tokens": tokens(raw),
                 "retained_tokens": tokens(memory), "truncated": tokens(raw) > budget,
                 "finished_at": stamp()}
    except Exception as exc:
        value = failure("compression", meta, exc)
    write(path, value)


def answer(client, model, bundle, question, condition, ratio, root):
    qid = question["question_id"]
    path = answer_path(root, condition, ratio, qid)
    if reusable(path, model):
        return path
    if condition == "full_context":
        context = bundle["context"]
    else:
        try:
            memory = read(memory_path(root, ratio, bundle))
            context = memory["memory"] if memory.get("status") == "ok" else None
        except Exception:
            context = None
        if context is None:
            write(path, failure("reader", {"type": "answer", "condition": condition, "question_id": qid},
                                RuntimeError("memory unavailable")))
            return path
    meta = {"type": "answer", "model": model, "condition": condition, "ratio": ratio,
            "question_id": qid, "context_id": bundle["context_id"], "goal_id": bundle["goal_id"]}
    prompt = fill(template("reader.txt"), context=context, question=question["question"])
    try:
        value = {**meta, "status": "ok", "answer": client.chat(model, prompt), "finished_at": stamp()}
    except Exception as exc:
        value = failure("reader", meta, exc)
    write(path, value)
    return path


def judge(client, model, bundle, question, condition, ratio, root):
    qid = question["question_id"]
    path = judgment_path(root, condition, qid)
    if reusable(path, model):
        return path
    meta = {"type": "judgment", "model": model, "condition": condition, "ratio": ratio, "question_id": qid}
    try:
        answer_value = read(answer_path(root, condition, ratio, qid))
        if answer_value.get("status") != "ok":
            raise RuntimeError("reader failed")
        gold = question.get("gold_answer", question.get("original_gold_answer", ""))
        prompt = fill(template("judge.txt"),
                      question=json.dumps(question["question"], ensure_ascii=False),
                      source_context=json.dumps(bundle["context"], ensure_ascii=False),
                      ground_truth=json.dumps(gold, ensure_ascii=False),
                      candidate_answer=json.dumps(answer_value["answer"], ensure_ascii=False))
        raw = client.chat(model, prompt)
        clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I | re.S).strip()
        parsed = json.loads(clean)
        if parsed.get("grade") not in {"CORRECT", "INCORRECT"}:
            raise ValueError("invalid judge grade")
        value = {**meta, "status": "ok", "grade": parsed["grade"],
                 "reason": parsed.get("reason", ""), "raw_response": raw, "finished_at": stamp()}
    except Exception as exc:
        value = failure("judge", meta, exc)
    write(path, value)


def parallel(items, fn, workers, label):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fn, item) for item in items]
        total = len(futures)
        for done, future in enumerate(as_completed(futures), 1):
            future.result()
            filled = int(30 * done / total) if total else 30
            print(f"\r{label} [{'#' * filled}{'.' * (30 - filled)}] {done}/{total}", end="", flush=True)
        if total:
            print()


def results(root, bundles, condition):
    rows = []
    for bundle in bundles:
        for question in bundle["questions"]:
            path = judgment_path(root, condition, question["question_id"])
            rows.append((read(path) if path.exists() else {"status": "failed"}, bundle))
    return rows


def goal_result(root, bundle, condition):
    questions = []
    for question in bundle["questions"]:
        path = judgment_path(root, condition, question["question_id"])
        result = read(path) if path.exists() else {"status": "failed", "error": "missing judgment"}
        item = {"question_id": question["question_id"],
                "status": result.get("status", "failed")}
        if item["status"] == "ok":
            item["grade"] = result.get("grade")
        else:
            item["error"] = result.get("error", "judgment failed")
        questions.append(item)
    valid = all(item["status"] == "ok" for item in questions)
    correct = valid and all(item.get("grade") == "CORRECT" for item in questions)
    return {"status": "correct" if correct else "incorrect" if valid else "invalid",
            "valid": valid, "correct": correct, "questions": questions}


def usage_entry(root, bundle, ratio):
    source_tokens = tokens(bundle["context"])
    budget = max(1, math.floor(source_tokens * ratio))
    entry = {"status": "missing", "source_tokens": source_tokens,
             "budget_tokens": budget, "retained_tokens": None, "usage_ratio": None}
    path = memory_path(root, ratio, bundle)
    if not path.exists():
        return entry
    try:
        value = read(path)
        entry["status"] = value.get("status", "failed")
        if entry["status"] == "ok":
            retained = value.get("retained_tokens")
            if isinstance(retained, (int, float)):
                entry["retained_tokens"] = retained
                entry["usage_ratio"] = retained / budget if budget else None
    except Exception as exc:
        entry["status"] = "failed"
        entry["error"] = str(exc)
    return entry


def compression_usage(root, bundles):
    output = {}
    for ratio in RATIOS:
        entries = [usage_entry(root, bundle, ratio) for bundle in bundles]
        valid = [entry for entry in entries if entry["retained_tokens"] is not None]
        output[f"{percent(ratio)}%"] = {
            "planned": len(entries),
            "valid": len(valid),
            "average_budget_tokens": sum(entry["budget_tokens"] for entry in entries) / len(entries)
            if entries else None,
            "average_retained_tokens": sum(entry["retained_tokens"] for entry in valid) / len(valid)
            if valid else None,
            "average_usage_ratio": sum(entry["usage_ratio"] for entry in valid) / len(valid)
            if valid else None,
        }
    return output


def summarize(rows):
    question_correct = sum(r.get("status") == "ok" and r.get("grade") == "CORRECT" for r, _ in rows)
    question_valid = sum(r.get("status") == "ok" for r, _ in rows)
    question_failed = len(rows) - question_valid
    goals = {}
    for result, bundle in rows:
        goals.setdefault((bundle["context_id"], bundle["goal_id"]), []).append(result)
    valid_goals = [items for items in goals.values() if all(r.get("status") == "ok" for r in items)]
    goal_correct = sum(all(r.get("grade") == "CORRECT" for r in items) for items in valid_goals)
    goal_valid = len(valid_goals)
    question_total = len(rows)
    goal_total = len(goals)
    return {"questions": {"planned": len(rows), "evaluated": question_valid,
                           "correct": question_correct, "incorrect": question_total - question_correct,
                           "failed": question_failed},
            "goals": {"planned": goal_total, "evaluated": goal_valid, "correct": goal_correct,
                      "incorrect": goal_total - goal_correct, "failed": goal_total - goal_valid},
            "micro_accuracy": question_correct / question_total if question_total else None,
            "macro_accuracy": goal_correct / goal_total if goal_total else None}


def report(root, bundles, metadata, include_full_context):
    conditions = []
    if include_full_context:
        conditions.append(("full_context", None))
    conditions.extend((f"{percent(r)}%", r) for r in RATIOS)
    output = {**metadata, "goals": len(bundles),
              "questions": sum(len(b["questions"]) for b in bundles), "conditions": {},
              "compression_usage": compression_usage(root, bundles)}
    evaluations = {b["goal_id"]: {} for b in bundles}
    for condition, ratio in conditions:
        rows = results(root, bundles, condition)
        by_dataset = {d: summarize([(r, b) for r, b in rows if dataset(b["dataset"]) == d]) for d in DATASETS}
        overall = summarize(rows)
        output["conditions"][condition] = {"benchmarks": by_dataset, "overall": overall}
        for bundle in bundles:
            evaluations[bundle["goal_id"]][condition] = goal_result(root, bundle, condition)
    out = root / "reports"
    write(out / "metrics.json", output)
    write_jsonl(out / "results.jsonl",
                [{**bundle,
                  "compression_usage": {f"{percent(ratio)}%": usage_entry(root, bundle, ratio)
                                        for ratio in RATIOS},
                  "evaluation": evaluations[bundle["goal_id"]]}
                 for bundle in bundles])
    return output


def print_summary(output):
    def pct(value):
        return "-" if value is None else f"{100 * value:.2f}%"

    print("\n=== Evaluation summary ===")
    for condition, data in output["conditions"].items():
        print(f"\n[{condition}]")
        print(f"{'Benchmark':<12} {'Goals (correct/valid/total)':>28} {'Micro':>10} {'Macro':>10}")
        for name, metrics in data["benchmarks"].items():
            goals = metrics["goals"]
            if goals["planned"] == 0:
                continue
            goal_count = f"{goals['correct']}/{goals['evaluated']}/{goals['planned']}"
            print(f"{name:<12} {goal_count:>28}"
                  f" {pct(metrics['micro_accuracy']):>10}"
                  f" {pct(metrics['macro_accuracy']):>10}")
        overall = data["overall"]
        goals = overall["goals"]
        goal_count = f"{goals['correct']}/{goals['evaluated']}/{goals['planned']}"
        print(f"{'Overall':<12} {goal_count:>28}"
              f" {pct(overall['micro_accuracy']):>10}"
              f" {pct(overall['macro_accuracy']):>10}")
    usage = output.get("compression_usage", {})
    if usage:
        print("\n=== Compression token usage ===")
        print(f"{'Budget':<10} {'Valid/total':>12} {'Mean budget':>14}"
              f" {'Mean retained':>16} {'Mean usage':>12}")
        for condition, metrics in usage.items():
            def number(value):
                return "-" if value is None else f"{value:.2f}"
            count = f"{metrics['valid']}/{metrics['planned']}"
            print(f"{condition:<10} {count:>12}"
                  f" {number(metrics['average_budget_tokens']):>14}"
                  f" {number(metrics['average_retained_tokens']):>16}"
                  f" {number(metrics['average_usage_ratio'] * 100 if metrics['average_usage_ratio'] is not None else None):>11}%")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=ROOT / "data/GACC-Bench-final.jsonl")
    p.add_argument("--output", type=Path, default=Path.cwd() / "gacc_eval_run")
    p.add_argument("--compressor-url", required=True)
    p.add_argument("--compressor-key", required=True)
    p.add_argument("--compressor-model", required=True)
    p.add_argument("--reader-url", required=True)
    p.add_argument("--reader-key", required=True)
    p.add_argument("--reader-model", required=True)
    p.add_argument("--judge-url", required=True)
    p.add_argument("--judge-key", required=True)
    p.add_argument("--judge-model", required=True)
    p.add_argument("--budgets", type=parse_budgets, default=(0.05, 0.10),
                   help="comma-separated retention budgets as percentages, e.g. 1,2,5,10,20")
    p.add_argument("--limit", type=int, default=0, help="first N goal instances; 0 means all")
    p.add_argument("--workers", type=int, default=300)
    p.add_argument("--qps", type=float, default=10)
    p.add_argument("--max-attempts", type=int, default=30)
    p.add_argument("--retry-sleep", type=float, default=30)
    p.add_argument("--include-full-context", type=boolean, default=False,
                   metavar="true|false",
                   help="also evaluate the uncompressed context (default: false)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    global RATIOS
    RATIOS = args.budgets
    if args.limit < 0 or args.workers < 1 or args.max_attempts < 1 or args.retry_sleep < 0:
        p.error("limit, workers, and retry settings are invalid")
    input_path = args.input.resolve()
    bundles = load(input_path, args.limit or None)
    info = {"contexts": len({b["context_id"] for b in bundles}), "goals": len(bundles),
            "questions": sum(len(b["questions"]) for b in bundles),
            "compressor_model": args.compressor_model, "reader_model": args.reader_model,
            "judge_model": args.judge_model,
            "budgets": [percent(ratio) for ratio in RATIOS],
            "limit": args.limit or "all", "workers": args.workers,
            "include_full_context": args.include_full_context,
            "max_attempts": args.max_attempts, "retry_sleep": args.retry_sleep}
    print(json.dumps(info, ensure_ascii=False, indent=2), flush=True)
    if args.dry_run:
        return
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=True)
    compressor = Client(args.compressor_url, args.compressor_key,
                        args.qps, args.max_attempts, args.retry_sleep)
    reader = Client(args.reader_url, args.reader_key,
                    args.qps, args.max_attempts, args.retry_sleep)
    judge_client = Client(args.judge_url, args.judge_key,
                          args.qps, args.max_attempts, args.retry_sleep)
    all_questions = [(b, q) for b in bundles for q in b["questions"]]
    memories = [(b, ratio) for b in bundles for ratio in RATIOS]
    parallel(memories, lambda x: compress(compressor, args.compressor_model, x[0], x[1], root), args.workers, "compression")
    answers = [(b, q, "full_context", None) for b, q in all_questions] if args.include_full_context else []
    for ratio in RATIOS:
        answers.extend((b, q, f"{percent(ratio)}%", ratio) for b, q in all_questions)
    parallel(answers, lambda x: answer(reader, args.reader_model, x[0], x[1], x[2], x[3], root), args.workers, "reader")
    judgments = [(b, q, "full_context", None) for b, q in all_questions] if args.include_full_context else []
    for ratio in RATIOS:
        judgments.extend((b, q, f"{percent(ratio)}%", ratio) for b, q in all_questions)
    parallel(judgments, lambda x: judge(judge_client, args.judge_model, x[0], x[1], x[2], x[3], root), args.workers, "judge")
    metrics = report(root, bundles, {"compressor_model": args.compressor_model,
                                     "reader_model": args.reader_model, "judge_model": args.judge_model,
                                     "input": str(input_path),
                                     "input_sha256": sha256(input_path), "limit": args.limit or "all",
                                     "include_full_context": args.include_full_context,
                                     "budgets": [percent(r) for r in RATIOS],
                                     "denominator": "all_planned_cases",
                                     "prompt_sha256": {name: sha256(ROOT / "prompts" / name)
                                                       for name in ("compression.txt", "reader.txt", "judge.txt")}},
                    args.include_full_context)
    print_summary(metrics)
    print(json.dumps({"metrics": str(root / "reports/metrics.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
