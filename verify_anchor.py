#!/usr/bin/env python3
"""Verify a federal legislative history chain anchor against a chain file.

Usage:
    python3 verify_anchor.py --anchor anchor-latest.json --chain legislative_history.jsonl

Three checks:
  1. anchor self-consistency (fields present, format known)
  2. hash recomputation: rebuild the chain from rows, tip must match anchor
  3. prev_anchor linkage: if prev anchor file supplied, hashes must chain
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

KNOWN_FORMAT_VERSIONS = {1}


def row_hash(prev_hash: str, row_json: str) -> str:
    return hashlib.sha256((prev_hash + row_json).encode("utf-8")).hexdigest()[:16]


def canonical(row: dict) -> str:
    """Replicate the chain's exact hash preimage: row WITHOUT the hash field,
    serialized sort_keys + ensure_ascii=False (must match legislative_history.py)."""
    body = {k: v for k, v in row.items() if k != "hash"}
    return json.dumps(body, ensure_ascii=False, sort_keys=True)


def main():
    ap = argparse.ArgumentParser(description="Federal law chain anchor verifier")
    ap.add_argument("--anchor", required=True, help="anchor JSON file (e.g. anchor-latest.json)")
    ap.add_argument("--chain", required=True, help="chain JSONL file copy")
    ap.add_argument("--prev-anchor", help="previous anchor file (optional, checks anchor-chain linkage)")
    args = ap.parse_args()

    failures = []

    anchor = json.loads(Path(args.anchor).read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in Path(args.chain).read_text(encoding="utf-8").splitlines() if l.strip()]

    # 1. anchor self-consistency
    if anchor.get("format_version") not in KNOWN_FORMAT_VERSIONS:
        failures.append(f"unknown format_version: {anchor.get('format_version')}")
    for k in ("chain", "tip_event_id", "tip_hash", "total_events", "type_counts"):
        if k not in anchor:
            failures.append(f"anchor missing field: {k}")
    if anchor.get("chain") != "federal-legislative-history":
        failures.append(f"unexpected chain name: {anchor.get('chain')}")

    # 2. hash recomputation over the full chain
    prev = ""
    recomputed = []
    tip_row = None
    for r in rows:
        h = row_hash(prev, canonical(r))
        recomputed.append(h)
        if r.get("hash") != h:
            failures.append(f"hash mismatch at {r.get('event_id')}: "
                            f"declared={r.get('hash')} recomputed={h}")
        prev = h
        # 锚点可以是链中任意一环（发布时的链尾，链生长后成为中间环）：
        # 只要锚的tip落在链上且哈希重算match，锚即有效——不要求锚=当前链尾。
        if r.get("event_id") == anchor.get("tip_event_id"):
            tip_row = r
    if tip_row is None:
        failures.append(f"anchor tip_event_id {anchor.get('tip_event_id')} not found in chain")
    elif anchor["tip_hash"] != tip_row["hash"]:
        failures.append(f"anchor tip_hash {anchor.get('tip_hash')} != "
                        f"chain row {tip_row['event_id']} hash {tip_row['hash']}")
    # total_events 是锚生成时刻的快照——链天然只增不减，所以只有
    # 「锚看到的比链副本还多」才算异常（链副本缺行）；链比锚长是正常生长。
    if anchor.get("total_events") is not None and anchor["total_events"] > len(rows):
        failures.append(f"total_events {anchor['total_events']} > chain length {len(rows)} — "
                        f"chain copy missing events relative to anchor snapshot")

    # 3. anchor-chain linkage
    if args.prev_anchor:
        pa = json.loads(Path(args.prev_anchor).read_text(encoding="utf-8"))
        if anchor.get("prev_anchor_hash") != pa.get("tip_hash"):
            failures.append(f"prev_anchor_hash {anchor.get('prev_anchor_hash')} "
                            f"!= previous anchor tip_hash {pa.get('tip_hash')}")
        elif (anchor["tip_hash"] == pa["tip_hash"]
              and anchor["tip_event_id"] == pa.get("tip_event_id")):
            failures.append("anchor tip equals previous tip — no progress since last publish")
    elif anchor.get("prev_anchor_hash") is not None:
        print(f"[info] prev_anchor_hash={anchor['prev_anchor_hash']} — "
              f"pass --prev-anchor to verify linkage")

    if failures:
        print("❌ ANCHOR VERIFICATION FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("✅ ANCHOR VERIFIED")
    print(f"  chain:     {anchor['chain']} (format v{anchor['format_version']})")
    print(f"  tip:       {anchor['tip_event_id']} @ {anchor['tip_hash']} ({anchor.get('tip_date', 'n/a')})")
    print(f"  events:    {anchor['total_events']}  types: {anchor['type_counts']}")
    print(f"  recomputation: {len(rows)} rows, all hashes match declared chain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
