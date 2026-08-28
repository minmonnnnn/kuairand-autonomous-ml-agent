# Runbook · Local Setup

Target: from nothing to a verified harness in about 15 minutes.

## 1. Environment

Python 3.9+. The official baseline path needs **numpy and nothing else** — no torch,
no pandas, no sklearn.

```bash
git clone <REPO_URL>
cd kuairand-autonomous-ml-agent
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Dataset

Downloaded from Zenodo, no registration needed. **Never commit it** — it is git-ignored.

```bash
wget https://zenodo.org/records/10439422/files/KuaiRand-Pure.tar.gz
tar xzf KuaiRand-Pure.tar.gz         # produces ./KuaiRand-Pure/
```

Expected files in `KuaiRand-Pure/data/`:

```text
log_standard_4_08_to_4_21_pure.csv     train window
log_standard_4_22_to_5_08_pure.csv     valid + test windows
log_random_4_22_to_5_08_pure.csv       random-exposure log (unbiased validation, advanced)
user_features_pure.csv
video_features_basic_pure.csv
video_features_statistic_pure.csv
```

Then copy `.env.example` to `.env` and set `KUAIRAND_DATA_DIR`.

## 3. Verify the harness — do this before anything else

```bash
cd starter_kit
python3 baseline.py --model random --data_dir ../KuaiRand-Pure/data
```

Expected: test Primary ≈ **0.4753** (±0.001), valid Primary ≈ **0.4834**.

If you do not get this, **stop**. Your harness is broken and every number you produce
afterwards will be wrong. The organizers call this out explicitly as the first check.

Also confirm the split sizes printed at load time:

```text
{'train': 1141112, 'valid': 124909, 'test': 170588}
```

## 4. Verify the official baseline

```bash
python3 baseline.py --model fm --data_dir ../KuaiRand-Pure/data
```

~40 seconds on one CPU core. Expected valid Primary ≈ **0.6016**, test ≈ **0.5946**.
Seed std is 0.0008, so a couple of points in the fourth decimal is fine.

## 5. Verify the repo's own tests

```bash
cd ..
pytest -q -m "not requires_data"     # no dataset needed
pytest -q                            # everything, needs the dataset
ruff check src tests
```

## 6. Set up your branch

```bash
git checkout -b <yourname>/<workstream>    # e.g. rishi/features
```

Then open `docs/coordination/TASK_BOARD.md` and find your `P0` task.

## Troubleshooting

**Row counts don't match.** You have the wrong dataset variant. This is KuaiRand-**Pure**,
not 1K or 27K.

**`ModuleNotFoundError: data`** when importing the starter kit — run from inside
`starter_kit/`, or use the adapter in `src/data/` which handles the path.

**Random gives ≈ 0.5 Primary instead of 0.475.** You are probably evaluating globally
instead of within-user, or you have modified `evaluate.py`. Restore it from git.

**FM is much slower than 40s.** Check that numpy is using a real BLAS, and that you are
not accidentally running on the 27K dataset.
