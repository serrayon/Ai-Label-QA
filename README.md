# AI Label QA Checker (Spanish)

Can an AI model label Spanish tweets as reliably as a trained human rater, and where does it fail?

This project measures that the way a data quality team would: build a human-audited gold set, have Claude label the same items from a written guideline, measure agreement, review every disagreement, improve the guideline, and measure again.

**Author:** Octavio Serrano, AI data quality lead and native Spanish speaker.

## How it works

1. **Gold set** (`prepare_data.py`): sample 200 tweets from a public Spanish sentiment dataset ([cardiffnlp/tweet_sentiment_multilingual](https://huggingface.co/datasets/cardiffnlp/tweet_sentiment_multilingual)). I audit every dataset label against the guideline and correct the ones I disagree with, logging each change.
2. **AI pre-labeling** (`label_with_claude.py`): Claude reads `guideline.md` and labels each tweet with a reason and a confidence score.
3. **Measurement** (`evaluate.py`): accuracy, Cohen's kappa, precision and recall per label, a confusion matrix, accuracy by confidence, and a list of every disagreement.
4. **Calibration loop**: I review the disagreements, decide whether the AI, the gold label or the guideline is wrong, update the guideline (`guideline_v2.md`), and re-run to measure the change.

## Results

_Fill this in after your runs._

| Run | Guideline | Model | Accuracy | Cohen's kappa |
|---|---|---|---|---|
| v1 | guideline.md | claude-haiku-5-5 | | |
| v2 | guideline_v2.md | claude-haiku-5-5 | | |

**Gold-set audit:** I corrected __ of 200 dataset labels (__%). Most common reason: __.

**What the AI got wrong most:** __ (for example, sarcasm, regional slang, news headlines).

**What I changed in the guideline:** __

**Routing recommendation:** items with AI confidence below __ had __% accuracy and should go to human review; above __, accuracy was __%.

## Run it yourself

Requires Python 3.10+.

```bash
pip install -r requirements.txt

# 1. Build the sample, then audit data/sample.csv by hand
python prepare_data.py

# 2. Test the pipeline without an API key (fake labels)
python label_with_claude.py --run mock --mock
python evaluate.py --run mock

# 3. Real run with Claude (set ANTHROPIC_API_KEY first)
python label_with_claude.py --run v1 --limit 10   # try 10 first
python label_with_claude.py --run v1              # then the rest
python evaluate.py --run v1

# 4. After improving the guideline
python label_with_claude.py --run v2 --guideline guideline_v2.md
python evaluate.py --run v2 --compare v1
```

Reports are written to `reports/`. A full 200-tweet run with Claude Haiku costs a few cents.

## Skills shown

Gold-set creation and auditing, guideline writing, inter-rater agreement (Cohen's kappa), error analysis, LLM-assisted labeling with prompt design, confidence-based routing to human review, and Python data analysis (pandas, scikit-learn).
