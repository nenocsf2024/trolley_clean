#!/usr/bin/env python3
"""
Phase 2 runner for hosted APIs (Anthropic, OpenAI, Mistral, Google Gemini, xAI Grok).

Reads a shortlist of scenarios, queries each provider for N stochastic samples,
and stores outputs in results/phase2/{provider}.jsonl plus a consolidated CSV.

Environment variables required:
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  MISTRAL_API_KEY
  GOOGLE_API_KEY         (Gemini 2.5 Flash Lite)
  XAI_API_KEY            (Grok-3)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
SCENARIO_PATH = BASE_DIR / "moral_core_21_sample.jsonl"
SHORTLIST_PATH = BASE_DIR / "results" / "local_runs" / "phase1_shortlist.csv"
OUTPUT_DIR = BASE_DIR / "results" / "phase2"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_ITERATIONS = 5
DEFAULT_TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 800
DEFAULT_SLEEP = 0.5

SYSTEM_PROMPT = (
    "You are a careful policy analyst. Provide a direct answer, explaining the primary "
    "value trade-off you are endorsing and why. Avoid bullet-point restatements unless "
    "they add clarity."
)

SCENARIO_IDS = [
    "MC21-005-F",
    "MC21-005-N",
    "MC21-002-S",
    "MC21-006-F",
    "MC21-003-N",
    "MC21-007-N",
]


def load_selected_scenarios() -> Dict[str, Dict[str, str]]:
    """Load scenario metadata and prompt for the shortlisted IDs."""
    data: Dict[str, Dict[str, str]] = {}
    if not SCENARIO_PATH.exists():
        raise FileNotFoundError(f"Scenario file not found: {SCENARIO_PATH}")

    with SCENARIO_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            sid = payload["id"]
            if sid in SCENARIO_IDS:
                data[sid] = {
                    "topic": payload.get("topic", ""),
                    "value_pair": payload.get("value_pair", ""),
                    "framing": payload.get("framing", ""),
                    "prompt": payload.get("prompt_text") or payload.get("prompt") or "",
                }
    missing = [sid for sid in SCENARIO_IDS if sid not in data]
    if missing:
        raise ValueError(f"Missing scenarios in dataset: {missing}")
    return data


def load_shortlist_notes() -> Dict[str, Dict[str, str]]:
    """Optional manual notes from phase1_shortlist.csv keyed by scenario_id."""
    notes: Dict[str, Dict[str, str]] = {}
    if not SHORTLIST_PATH.exists():
        return notes
    with SHORTLIST_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["scenario_id"]
            notes.setdefault(sid, {})
            notes[sid][row["model"]] = row.get("quality_notes", "")
    return notes


def anthropic_completion(prompt: str, temperature: float) -> str:
    url = "https://api.anthropic.com/v1/messages"
    api_key = os.environ["ANTHROPIC_API_KEY"]
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": temperature,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def openai_completion(prompt: str, temperature: float) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    api_key = os.environ["OPENAI_API_KEY"]
    project = os.getenv("OPENAI_PROJECT")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if project:
        headers["OpenAI-Project"] = project
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def mistral_completion(prompt: str, temperature: float) -> str:
    url = "https://api.mistral.ai/v1/chat/completions"
    api_key = os.environ["MISTRAL_API_KEY"]
    payload = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def gemini_completion(prompt: str, temperature: float) -> str:
    api_key = os.environ["GOOGLE_API_KEY"]
    model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model_id}:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": min(MAX_OUTPUT_TOKENS, 512),
            "responseMimeType": "text/plain",
        },
    }
    resp = requests.post(url, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise ValueError(f"Unexpected Gemini response: {data}")


def grok_completion(prompt: str, temperature: float) -> str:
    url = "https://api.x.ai/v1/chat/completions"
    api_key = os.environ["XAI_API_KEY"]
    payload = {
        "model": "grok-3-latest",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": MAX_OUTPUT_TOKENS,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


@dataclass
class ModelConfig:
    name: str
    provider: str
    completion_fn: Callable[[str, float], str]


def get_model_configs() -> List[ModelConfig]:
    return [
        ModelConfig("claude-sonnet-4-20250514", "anthropic", anthropic_completion),
        ModelConfig(os.getenv("OPENAI_MODEL", "gpt-4o"), "openai", openai_completion),
        ModelConfig("mistral-large-latest", "mistral", mistral_completion),
        ModelConfig(os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"), "google", gemini_completion),
        ModelConfig("grok-3-latest", "xai", grok_completion),
    ]


def select_model_configs(include_providers: Optional[List[str]] = None,
                         include_models: Optional[List[str]] = None) -> List[ModelConfig]:
    configs = get_model_configs()
    if include_providers:
        providers = {p.strip() for p in include_providers if p.strip()}
        configs = [cfg for cfg in configs if cfg.provider in providers]
    if include_models:
        models = {m.strip() for m in include_models if m.strip()}
        configs = [cfg for cfg in configs if cfg.name in models]
    if not configs:
        raise ValueError("No models selected after applying filters.")
    return configs


def load_env_from_dotenv(dotenv_path: Path) -> None:
    """
    Minimal .env loader so users can define API keys without exporting manually.

    Lines in KEY=VALUE format are added to os.environ if the key is not set already.
    """
    if not dotenv_path.exists():
        return
    with dotenv_path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def run_phase2(
    iterations: int,
    temperature: float,
    configs: List[ModelConfig],
    sleep_seconds: float,
) -> None:
    load_env_from_dotenv(BASE_DIR / ".env")
    scenarios = load_selected_scenarios()
    notes = load_shortlist_notes()

    summary_rows: List[Dict[str, str]] = []

    for model_cfg in configs:
        model_slug = model_cfg.name.replace(":", "_").replace(".", "_")
        out_path = OUTPUT_DIR / f"{model_slug}.jsonl"
        print(f"\n=== Running {model_cfg.name} ({model_cfg.provider}) ===")

        with out_path.open("w", encoding="utf-8") as out_f:
            for scenario_id in SCENARIO_IDS:
                prompt = scenarios[scenario_id]["prompt"]
                context = scenarios[scenario_id]

                for iteration in range(1, iterations + 1):
                    jitter = temperature + random.uniform(-0.05, 0.05)
                    jitter = max(0.0, min(2.0, jitter))
                    t0 = time.time()
                    try:
                        response_text = model_cfg.completion_fn(prompt, jitter)
                        latency = time.time() - t0
                        record = {
                            "scenario_id": scenario_id,
                            "iteration": iteration,
                            "model": model_cfg.name,
                            "provider": model_cfg.provider,
                            "temperature_used": jitter,
                            "latency_s": round(latency, 3),
                            "response": response_text,
                            "topic": context["topic"],
                            "value_pair": context["value_pair"],
                            "framing": context["framing"],
                            "notes_phase1": notes.get(scenario_id, {}).get(model_cfg.name, ""),
                        }
                        out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                        summary_rows.append(
                            {
                                "model": model_cfg.name,
                                "provider": model_cfg.provider,
                                "scenario_id": scenario_id,
                                "iteration": iteration,
                                "latency_s": f"{latency:.3f}",
                                "tokens_prompt_est": "NA",
                                "tokens_completion_est": "NA",
                            }
                        )
                        print(
                            f"{model_cfg.name} [{scenario_id}] iter {iteration} "
                            f"(latency {latency:.2f}s)"
                        )
                    except Exception as exc:  # noqa: BLE001
                        latency = time.time() - t0
                        error_record = {
                            "scenario_id": scenario_id,
                            "iteration": iteration,
                            "model": model_cfg.name,
                            "provider": model_cfg.provider,
                            "temperature_used": jitter,
                            "latency_s": round(latency, 3),
                            "error": str(exc),
                            "topic": context["topic"],
                            "value_pair": context["value_pair"],
                            "framing": context["framing"],
                        }
                        out_f.write(json.dumps(error_record, ensure_ascii=False) + "\n")
                        summary_rows.append(
                            {
                                "model": model_cfg.name,
                                "provider": model_cfg.provider,
                                "scenario_id": scenario_id,
                                "iteration": iteration,
                                "latency_s": f"{latency:.3f}",
                                "tokens_prompt_est": "NA",
                                "tokens_completion_est": "NA",
                                "error": str(exc),
                            }
                        )
                        print(
                            f"[ERROR] {model_cfg.name} [{scenario_id}] iter {iteration}: {exc}"
                        )
                    time.sleep(sleep_seconds)

    summary_path = OUTPUT_DIR / "phase2_runs_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "model",
            "provider",
            "scenario_id",
            "iteration",
            "latency_s",
            "tokens_prompt_est",
            "tokens_completion_est",
            "error",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            row.setdefault("error", "")
            writer.writerow(row)
    print(f"\nWrote summary to {summary_path}")


def smoke_test(configs: List[ModelConfig], sleep_seconds: float) -> None:
    """Fire a single minimal request to each provider to verify credentials."""
    load_env_from_dotenv(BASE_DIR / ".env")
    prompt = "Please reply with a single short greeting."
    for cfg in configs:
        print(f"\nTesting {cfg.name} ({cfg.provider})...")
        try:
            response = cfg.completion_fn(prompt, temperature=0.0)
            print(f"✓ {cfg.provider}: {response.strip()[:120]}")
        except Exception as exc:  # noqa: BLE001
            print(f"✗ {cfg.provider} error: {exc}")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 2 API runner")
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Samples per scenario (default {DEFAULT_ITERATIONS})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Base temperature (default {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--providers",
        type=str,
        default="",
        help="Comma-separated list of providers to include (e.g. 'google,openai')",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="",
        help="Comma-separated list of model IDs to include (takes precedence over providers)",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Send a single short prompt to each provider to verify credentials.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=DEFAULT_SLEEP,
        help=f"Delay in seconds between requests (default {DEFAULT_SLEEP})",
    )
    args = parser.parse_args()

    include_providers = [p.strip() for p in args.providers.split(",") if p.strip()] or None
    include_models = [m.strip() for m in args.models.split(",") if m.strip()] or None
    configs = select_model_configs(include_providers, include_models)

    if args.smoke_test:
        smoke_test(configs, sleep_seconds=args.sleep)
    else:
        run_phase2(iterations=args.iterations, temperature=args.temperature, configs=configs, sleep_seconds=args.sleep)
