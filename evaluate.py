"""
Step 3: Measure how well the AI labels agree with your gold set.

Compares results/ai_labels_<run>.csv with the gold_label column in data/sample.csv and
writes reports/report_<run>.md with:
  - accuracy and Cohen's kappa (agreement beyond chance, the standard inter-rater metric)
  - precision and recall per label
  - a confusion matrix (which labels get mixed up)
  - how accuracy changes with the model's confidence
  - every disagreement, so you can review them and improve the guideline

Usage:
  python evaluate.py --run v1
  python evaluate.py --run v2 --compare v1     # show the change between two runs
"""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, cohen_kappa_score, confusion_matrix

LABELS = ["negative", "neutral", "positive"]


def load(run, data_path):
    gold = pd.read_csv(data_path, encoding="utf-8")
    ai = pd.read_csv(Path("results") / f"ai_labels_{run}.csv", encoding="utf-8")
    df = gold.merge(ai, on="id", how="inner")
    errors = (df["ai_label"] == "error").sum()
    return df[df["ai_label"] != "error"].copy(), errors


def metrics(df):
    return {
        "n": len(df),
        "accuracy": accuracy_score(df["gold_label"], df["ai_label"]),
        "kappa": cohen_kappa_score(df["gold_label"], df["ai_label"]),
    }


def kappa_words(k):
    # Landis & Koch (1977) interpretation scale
    if k < 0.2:
        return "slight"
    if k < 0.4:
        return "fair"
    if k < 0.6:
        return "moderate"
    if k < 0.8:
        return "substantial"
    return "almost perfect"


def table(rows, header):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--compare", default=None, help="an earlier run to compare against")
    parser.add_argument("--data", default="data/sample.csv")
    args = parser.parse_args()

    df, errors = load(args.run, args.data)
    m = metrics(df)
    out = [f"# AI label QA report: run `{args.run}`", ""]

    # Headline numbers
    out += ["## Agreement with the gold set", ""]
    out += [table([[m["n"], f"{m['accuracy']:.1%}", f"{m['kappa']:.3f} ({kappa_words(m['kappa'])})", errors]],
                  ["Items", "Accuracy", "Cohen's kappa", "API errors"]), ""]

    if args.compare:
        prev, _ = load(args.compare, args.data)
        p = metrics(prev)
        out += [f"Change from `{args.compare}`: accuracy {p['accuracy']:.1%} to {m['accuracy']:.1%} "
                f"({(m['accuracy'] - p['accuracy']) * 100:+.1f} pts), "
                f"kappa {p['kappa']:.3f} to {m['kappa']:.3f}.", ""]

    # Gold-set audit summary
    changed = (df["original_label"] != df["gold_label"]).sum()
    out += ["## Gold-set audit", "",
            f"You changed {changed} of {len(df)} dataset labels ({changed / len(df):.1%}) during your review.", ""]

    # Per-label precision / recall
    rep = classification_report(df["gold_label"], df["ai_label"], labels=LABELS, output_dict=True, zero_division=0)
    rows = [[lab, f"{rep[lab]['precision']:.2f}", f"{rep[lab]['recall']:.2f}", f"{rep[lab]['f1-score']:.2f}",
             int(rep[lab]["support"])] for lab in LABELS]
    out += ["## By label", "", table(rows, ["Label", "Precision", "Recall", "F1", "Gold count"]), ""]

    # Confusion matrix
    cm = confusion_matrix(df["gold_label"], df["ai_label"], labels=LABELS)
    rows = [[f"gold: {LABELS[i]}"] + list(cm[i]) for i in range(len(LABELS))]
    out += ["## Confusion matrix", "", "Rows are your gold labels; columns are the AI's labels.", "",
            table(rows, [""] + [f"AI: {lab}" for lab in LABELS]), ""]

    # Confidence calibration: is the model right more often when it says it's sure?
    df["correct"] = df["gold_label"] == df["ai_label"]
    bins = pd.cut(df["ai_confidence"].astype(float), [0, 0.6, 0.8, 0.9, 1.0], include_lowest=True,
                  labels=["0 to 0.6", "0.6 to 0.8", "0.8 to 0.9", "0.9 to 1.0"])
    cal = df.groupby(bins, observed=True)["correct"].agg(["count", "mean"]).reset_index()
    rows = [[str(r["ai_confidence"]), int(r["count"]), f"{r['mean']:.1%}"] for _, r in cal.iterrows()]
    out += ["## Accuracy by AI confidence", "",
            "If accuracy rises with confidence, low-confidence items are the ones to route to human review.", "",
            table(rows, ["Confidence", "Items", "Accuracy"]), ""]

    # Every disagreement, for review
    wrong = df[~df["correct"]].sort_values("ai_confidence", ascending=False)
    rows = [[r.id, str(r.text).replace("|", "/").replace("\n", " ")[:140], r.gold_label, r.ai_label,
             r.ai_confidence, str(r.ai_reason).replace("|", "/")[:120]] for r in wrong.itertuples()]
    out += [f"## Disagreements ({len(wrong)})", "",
            "Review these: is the AI wrong, is the gold label wrong, or is the guideline unclear?", "",
            table(rows, ["ID", "Tweet", "Gold", "AI", "Conf.", "AI reason"]), ""]

    Path("reports").mkdir(exist_ok=True)
    path = Path("reports") / f"report_{args.run}.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Accuracy {m['accuracy']:.1%}, kappa {m['kappa']:.3f} ({kappa_words(m['kappa'])}) on {m['n']} items")
    print(f"Report written to {path}")


if __name__ == "__main__":
    main()
