#!/usr/bin/env python3
"""Evidence-bounded post-cluster LLM interpretation.

The script intentionally receives only pre-computed cluster evidence. It does
not perform clustering and does not have access to the frozen reference-theme
inventory, GT labels, expert scores, or final research-gap decisions.

By default the script is a dry run. Add --execute to make an API request.
Generated JSONL records are compatible with the repeated-run stability script;
a later blinded human-review step may append a `human_decision` field before
decision-invariance analysis.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import yaml


def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_user_message(template: str, args: argparse.Namespace) -> str:
    return template.format(
        cluster_id=args.cluster_id,
        corpus=args.corpus,
        top_c_tfidf_terms="; ".join(args.terms),
        representative_record_1=args.records[0],
        representative_record_2=args.records[1],
        representative_record_3=args.records[2],
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster-id", required=True)
    parser.add_argument("--corpus", choices=["academic", "public"], default="academic")
    parser.add_argument("--terms", nargs="+", required=True, help="c-TF-IDF terms supplied to the fixed prompt")
    parser.add_argument("--records", nargs=3, required=True, help="Exactly three representative de-identified records")
    parser.add_argument("--config", default="config/paper_config.yaml")
    parser.add_argument("--system-prompt", default="prompts/system_prompt.txt")
    parser.add_argument("--user-template", default="prompts/user_template.txt")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run identifier for repeated-generation ledgers. Defaults to the decoding seed.",
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--output", default=None, help="Optional JSONL ledger to append the generated result")
    args = parser.parse_args()

    cfg = load_config(args.config)
    llm_cfg = cfg["llm"]
    system_prompt = load_text(args.system_prompt)
    user_template = load_text(args.user_template)
    user_message = build_user_message(user_template, args)
    seed = llm_cfg["seed"] if args.seed is None else args.seed
    run_id = str(seed) if args.run_id is None else str(args.run_id)

    if len(args.terms) != int(cfg["ctfidf"]["top_n_terms"]):
        print(
            f"WARNING: supplied {len(args.terms)} terms; the reported study used "
            f"{cfg['ctfidf']['top_n_terms']} c-TF-IDF terms per unit. "
            "This is acceptable for a dry-run schema demonstration but is not paper-equivalent input."
        )

    payload_preview = {
        "model": llm_cfg["model"],
        "temperature": llm_cfg["temperature"],
        "top_p": llm_cfg["top_p"],
        "seed": seed,
        "max_tokens": llm_cfg["max_tokens"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }

    audit_metadata = {
        "unit_id": args.cluster_id,
        "cluster_id": args.cluster_id,
        "corpus": args.corpus,
        "run_id": run_id,
        "seed": seed,
        "model": llm_cfg["model"],
        "temperature": llm_cfg["temperature"],
        "top_p": llm_cfg["top_p"],
        "max_tokens": llm_cfg["max_tokens"],
        "system_prompt_sha256": sha256_text(system_prompt),
        "user_message_sha256": sha256_text(user_message),
    }

    if not args.execute:
        print(json.dumps({"audit_metadata": audit_metadata, "payload": payload_preview}, indent=2, ensure_ascii=False))
        print("\nDRY RUN: no API request was made.")
        return

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required when --execute is used")

    from openai import OpenAI

    client = OpenAI()
    last_error: Exception | None = None
    result: dict | None = None

    for _attempt in range(int(llm_cfg.get("max_json_retries", 2)) + 1):
        try:
            response = client.chat.completions.create(
                model=llm_cfg["model"],
                messages=payload_preview["messages"],
                temperature=llm_cfg["temperature"],
                top_p=llm_cfg["top_p"],
                seed=seed,
                max_tokens=llm_cfg["max_tokens"],
                response_format={"type": "json_object"},
            )
            text = response.choices[0].message.content or "{}"
            result = json.loads(text)
            break
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc

    if result is None:
        raise RuntimeError(f"No valid JSON response after retries: {last_error}")

    required_keys = {
        "provisional_label",
        "two_sentence_summary",
        "supporting_terms",
        "alternative_label",
        "uncertainty",
        "prohibited_claim_check",
    }
    missing = required_keys.difference(result)
    if missing:
        raise ValueError(
            "A syntactically valid JSON object was returned but required schema keys are missing: "
            f"{sorted(missing)}. The manuscript's retry rule applies only to invalid JSON, so the response is not semantically rewritten."
        )

    record = {**audit_metadata, **result}

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Appended result to {path}")
    else:
        print(json.dumps(record, indent=2, ensure_ascii=False))

    print(
        "Reminder: this output remains provisional. It does not become a reportable proposition without "
        "document-level trace evidence, recorded human adjudication, and independent expert confirmation."
    )


if __name__ == "__main__":
    main()
