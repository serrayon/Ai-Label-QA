"""
Step 1: Build the gold-set sample.

Downloads a public Spanish tweet sentiment dataset (cardiffnlp/tweet_sentiment_multilingual,
Spanish test split), takes a random sample, and saves it as data/sample.csv.

The dataset's original label goes in two columns:
  - original_label: what the dataset says (never edit this)
  - gold_label:     YOUR answer. Review every row and fix it where you disagree.
                    Log each change in the 'gold_note' column. That audit is the human
                    gold-set work this project is built on.

Usage:
  python prepare_data.py              # 200 tweets
  python prepare_data.py --n 300      # a different sample size
"""
import argparse
from pathlib import Path

import pandas as pd
from datasets import load_dataset

LABEL_NAMES = {0: "negative", 1: "neutral", 2: "positive"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200, help="number of tweets to sample")
    parser.add_argument("--seed", type=int, default=42, help="random seed, so the sample is repeatable")
    args = parser.parse_args()

    ds = load_dataset("cardiffnlp/tweet_sentiment_multilingual", "spanish", split="test")
    df = ds.to_pandas()
    df["original_label"] = df["label"].map(LABEL_NAMES)

    # Balanced-ish sample: roughly equal counts of each label, so every class gets tested
    per_class = max(1, args.n // 3)
    # (a plain loop instead of groupby().apply, which drops the label column in pandas 3)
    sample = (
        pd.concat([g.sample(min(len(g), per_class), random_state=args.seed)
                   for _, g in df.groupby("original_label")])
        .sample(frac=1, random_state=args.seed)  # shuffle
        .reset_index(drop=True)
    )

    sample.insert(0, "id", [f"t{i:04d}" for i in range(len(sample))])
    sample["gold_label"] = sample["original_label"]  # start from the dataset label, then audit it
    sample["gold_note"] = ""
    out = sample[["id", "text", "original_label", "gold_label", "gold_note"]]

    Path("data").mkdir(exist_ok=True)
    out.to_csv("data/sample.csv", index=False, encoding="utf-8")
    print(f"Saved {len(out)} tweets to data/sample.csv")
    print(out["original_label"].value_counts().to_string())
    print("\nNext: open data/sample.csv, review each gold_label against guideline.md,")
    print("fix any you disagree with, and explain each change in gold_note.")


if __name__ == "__main__":
    main()
