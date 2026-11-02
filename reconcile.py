#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json


def parse_ts(value):
    if value is None:
        return None
    try:
        return str(value)
    except Exception:
        return None


latest_by_txn = {}

with open("payments.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if txn_id is None or txn_id == "":
            continue

        previous = latest_by_txn.get(txn_id)
        if previous is None:
            latest_by_txn[txn_id] = event
            continue

        previous_ts = previous.get("ts")
        current_ts = event.get("ts")

        # Only the latest attempt for each txn_id should count.
        # ISO-8601 UTC timestamps compare correctly as strings.
        if current_ts is None:
            continue
        if previous_ts is None or current_ts > previous_ts or current_ts == previous_ts:
            latest_by_txn[txn_id] = event

count = 0
total = 0.0

for event in latest_by_txn.values():
    if event.get("status") == "success":
        count += 1
        try:
            total += float(event.get("amount", 0) or 0)
        except (TypeError, ValueError):
            pass

with open("expected.txt", "r", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
