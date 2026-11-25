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

No coding experience needed. Every command below is typed into a terminal: a window where you type commands instead of clicking. Copy each command, paste it into the terminal, and press Enter.

### Step 1: Install Python (once)

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest version (3.10 or newer).
2. Run the installer. **On Windows, tick "Add python.exe to PATH" on the first screen** before you click Install.
3. Check that it worked. Open a terminal:
   - **Mac:** press Cmd+Space, type `Terminal`, press Enter.
   - **Windows:** press the Windows key, type `PowerShell`, press Enter.

   Then type `python3 --version` (Mac) or `python --version` (Windows). You should see something like `Python 3.13.1`.

### Step 2: Get the project and open it in the terminal (once)

1. On this GitHub page, click the green **Code** button, then **Download ZIP**. Unzip it (double-click on Mac; right-click and **Extract All** on Windows).
2. In the terminal, go into the project folder. `cd` means "change folder":
   - **Mac:** type `cd ` (with a space), drag the unzipped folder from Finder into the terminal window, and press Enter.
   - **Windows:** open the unzipped folder in File Explorer, click the address bar, type `powershell`, and press Enter. A terminal opens already inside the folder.

### Step 3: Install the requirements (once)

This creates a private Python environment for the project (the `.venv` folder) so nothing on the rest of your computer is affected, then installs the four libraries listed in `requirements.txt`.

**Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

When it works, your terminal line starts with `(.venv)`. If Windows says "running scripts is disabled", run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y`, and try the activate line again.

**Every time you come back** to the project, open a terminal in the folder (Step 2) and run only the activate line (`source .venv/bin/activate` on Mac, `.venv\Scripts\Activate.ps1` on Windows). Once `(.venv)` shows, the command `python` works on both Mac and Windows.

### Step 4: Build the sample and audit it

```bash
python prepare_data.py
```

This downloads about 200 Spanish tweets and saves them to `data/sample.csv`. Open that file in Google Sheets (File, Import) or Excel. For each tweet, check `gold_label` against `guideline.md`. If you disagree, change it and write the reason in `gold_note`. Save it back as CSV: in Excel choose **CSV UTF-8**, in Google Sheets use **File, Download, CSV**. Ordinary CSV can garble accented letters like á and ñ.

### Step 5: Test the pipeline without an API key (optional)

```bash
python label_with_claude.py --run mock --mock
python evaluate.py --run mock
```

This uses fake labels, so the numbers mean nothing. It just proves everything runs. Open `reports/report_mock.md` to see what a report looks like.

### Step 6: Label with Claude

1. Create an API key at [console.anthropic.com](https://console.anthropic.com) (you need to add a few dollars of credit). Never share the key or put it in a file you upload.
2. Give the key to this terminal window (replace `sk-ant-...` with your key):
   - **Mac:** `export ANTHROPIC_API_KEY="sk-ant-..."`
   - **Windows:** `$env:ANTHROPIC_API_KEY="sk-ant-..."`

   This lasts until you close the window, so repeat it each session.
3. Run it, trying 10 tweets first:
```bash
python label_with_claude.py --run v1 --limit 10
python label_with_claude.py --run v1
python evaluate.py --run v1
```

Your report is `reports/report_v1.md`. A full run with Claude Haiku costs a few cents. If it stops partway, run the same command again; it picks up where it left off.

### Step 7: Improve the guideline and measure again

Review the disagreements at the bottom of the report. Copy `guideline.md` to `guideline_v2.md`, add rules for the mistakes you saw, then:

```bash
python label_with_claude.py --run v2 --guideline guideline_v2.md
python evaluate.py --run v2 --compare v1
```

### If something goes wrong

| Message | Fix |
|---|---|
| `python: command not found` or `python3: command not found` | Python isn't installed or wasn't added to PATH. Reinstall it (on Windows, tick "Add python.exe to PATH"), then open a new terminal. |
| `No module named pandas` (or anthropic, datasets, sklearn) | The environment isn't active. Run the activate line from Step 3 and look for `(.venv)`. |
| `No such file or directory: data/sample.csv` | You're in the wrong folder, or you haven't done Step 4. Go back to Step 2. |
| `Set ANTHROPIC_API_KEY first` | Do Step 6.2 again in this terminal window. |
| Accented letters look like `Ã±` | Re-save the CSV as UTF-8 (Step 4). |

## Skills shown

Gold-set creation and auditing, guideline writing, inter-rater agreement (Cohen's kappa), error analysis, LLM-assisted labeling with prompt design, confidence-based routing to human review, and Python data analysis (pandas, scikit-learn).
