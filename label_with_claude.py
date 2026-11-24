"""
Step 2: Have Claude pre-label every tweet using the guideline.

For each tweet, Claude reads guideline.md and returns a label, a short reason, and a
confidence score. Results go to results/ai_labels_<run>.csv. The script skips tweets it
has already labeled, so you can stop and restart it safely.

Setup (once):
  1. Create an API key at https://console.anthropic.com
  2. Set it in your terminal:
       Mac/Linux:  export ANTHROPIC_API_KEY="sk-ant-..."
       Windows:    setx ANTHROPIC_API_KEY "sk-ant-..."   (then open a new terminal)

Usage:
  python label_with_claude.py --run v1                      # label everything with guideline.md
  python label_with_claude.py --run v1 --limit 10           # try 10 tweets first
  python label_with_claude.py --run v2 --guideline guideline_v2.md   # after you improve the guideline
  python label_with_claude.py --run mock --mock             # no API key: fake labels, to test the pipeline
"""
import argparse
import json
import os
import random
import re
import time
from pathlib import Path

import pandas as pd

DEFAULT_MODEL = "claude-haiku-5-5"  # cheapest current Claude model; change with --model
LABELS = {"positive", "negative", "neutral"}

SYSTEM_TEMPLATE = """You are an expert annotator of Spanish-language social media.
Follow this labeling guideline exactly:

<guideline>
{guideline}
</guideline>

For the tweet you are given, reply with ONLY a JSON object, no other text:
{{"label": "positive" | "negative" | "neutral", "reason": "<one short sentence in English>", "confidence": <number from 0 to 1>}}"""


def parse_reply(text):
    """Pull the JSON object out of the model's reply and validate the label."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"no JSON in reply: {text[:200]}")
    data = json.loads(match.group(0))
    label = str(data.get("label", "")).strip().lower()
    if label not in LABELS:
        raise ValueError(f"invalid label: {label}")
    return label, str(data.get("reason", "")).strip(), float(data.get("confidence", 0))


def label_with_api(client, model, system, tweet, retries=3):
    for attempt in range(retries):
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=300,
                system=system,
                messages=[{"role": "user", "content": f"Tweet: {tweet}"}],
            )
            reply = "".join(block.text for block in msg.content if block.type == "text")
            return parse_reply(reply)
        except Exception as err:  # rate limits, network blips, bad JSON
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  retrying in {wait}s ({err})")
            time.sleep(wait)


def label_mock(tweet, rng):
    """Fake labeler for testing without an API key. Not a real model."""
    pos = ["bueno", "genial", "feliz", "gracias", "amo", "mejor", "chido", "orgullo"]
    neg = ["malo", "odio", "triste", "desastre", "peor", "asco", "nunca", "mierda"]
    t = tweet.lower()
    if any(w in t for w in pos):
        label = "positive"
    elif any(w in t for w in neg):
        label = "negative"
    else:
        label = "neutral"
    if rng.random() < 0.15:  # add some noise so the report has errors to show
        label = rng.choice(sorted(LABELS - {label}))
    return label, "mock keyword rule", round(rng.uniform(0.5, 0.95), 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="name for this run, e.g. v1")
    parser.add_argument("--guideline", default="guideline.md")
    parser.add_argument("--data", default="data/sample.csv")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=None, help="only label the first N tweets")
    parser.add_argument("--mock", action="store_true", help="use fake labels instead of the API")
    args = parser.parse_args()

    df = pd.read_csv(args.data, encoding="utf-8")
    if args.limit:
        df = df.head(args.limit)

    out_path = Path("results") / f"ai_labels_{args.run}.csv"
    out_path.parent.mkdir(exist_ok=True)
    done = pd.read_csv(out_path) if out_path.exists() else pd.DataFrame(columns=["id"])
    done_ids = set(done["id"])

    guideline = Path(args.guideline).read_text(encoding="utf-8")
    system = SYSTEM_TEMPLATE.format(guideline=guideline)

    client = None
    if not args.mock:
        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("Set ANTHROPIC_API_KEY first (see the top of this file), or use --mock.")
        client = anthropic.Anthropic()
    rng = random.Random(0)

    rows = done.to_dict("records")
    todo = df[~df["id"].isin(done_ids)]
    print(f"{len(done_ids)} already labeled, {len(todo)} to go (model: {'mock' if args.mock else args.model})")

    for i, row in enumerate(todo.itertuples(), start=1):
        try:
            if args.mock:
                label, reason, conf = label_mock(row.text, rng)
            else:
                label, reason, conf = label_with_api(client, args.model, system, row.text)
        except Exception as err:
            label, reason, conf = "error", str(err)[:200], 0.0
        rows.append({"id": row.id, "ai_label": label, "ai_reason": reason, "ai_confidence": conf})
        if i % 20 == 0 or i == len(todo):  # save progress regularly
            pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8")
            print(f"  {i}/{len(todo)} labeled")

    pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8")
    print(f"Saved {len(rows)} labels to {out_path}")


if __name__ == "__main__":
    main()
