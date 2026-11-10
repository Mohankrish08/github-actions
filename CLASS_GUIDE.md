# Class 4 Teaching Guide: Every Push Gets Checked Automatically

**Time:** about 2 hours
**Project:** the Class 3 taxi project, plus tests, a model check and a GitHub Actions workflow

## By the end of class, students can

1. Write tests for data cleaning and an API
2. Explain why ML needs a model check as well as code tests
3. Write a GitHub Actions workflow with jobs that run in order
4. Read a failed check, fix it, and get it green
5. Block a pull request from merging until the checks pass

## Before class

**You**
- [ ] Push this folder to a test repo on GitHub and watch all three jobs pass. **This workflow has not run on GitHub yet**
- [ ] Note how long each job takes, so you can tell students what to expect
- [ ] Try the merge-blocking ruleset (Part 7) on your test repo

**Students**
- [ ] GitHub account, Git installed, and Python 3.10 or above
- [ ] Set their Git name and email:
  ```
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  ```
- [ ] Push any small repo once, so the GitHub login is already done

## Class plan

| Time | Part | Outcome |
|---|---|---|
| 10 min | 1. Why automate? | Students see the problem CI solves |
| 20 min | 2. Read and run the tests | `13 passed` on their laptop |
| 15 min | 3. The model check | `PASSED` with error 3.32 |
| 15 min | 4. Read the workflow | Students understand jobs, steps and `needs` |
| 15 min | 5. Push and get green | Three green jobs on GitHub |
| 25 min | 6. Break it on purpose | Demo A and demo B fail for different reasons |
| 10 min | 7. Block bad merges | Red pull requests can't merge |
| 10 min | Wrap-up | Check understanding |

---

## Part 1: Why automate? (10 min)

**Ask:** "In Class 3, how did we stop a weak model from replacing the champion?"

**Answer:** we ran `retrain.py`, and it compared the models. That only worked because we remembered to run it.

**Say:** "On a team, many people push code every day. Nobody remembers every check. CI runs them for us, every time, on a clean machine."

**Key terms**

| Term | Simple meaning |
|---|---|
| CI (continuous integration) | Automatic checks on every push |
| Workflow | A YAML file in `.github/workflows/` that says what to run |
| Job | A group of steps that runs on a fresh machine |
| Step | One command or one ready-made action |
| Pull request (PR) | A request to merge a branch into `main`, where the checks run |

## Part 2: Read and run the tests (20 min)

```
pip install ".[test]"
pytest -v
```

Expected: `13 passed`.

**Walk through `tests/test_data.py`:** each test writes a tiny trip file, loads it with `load_month`, and checks the result.

| Test | Checks that |
|---|---|
| `test_keeps_a_normal_trip` | Good trips survive |
| `test_calculates_duration_hour_and_weekday` | The features are calculated correctly |
| `test_removes_a_trip_under_one_minute` | 0-minute trips are removed |
| `test_removes_a_trip_over_an_hour` | 90-minute trips are removed |
| `test_removes_a_trip_with_no_distance` | 0-mile trips are removed |
| `test_removes_a_trip_from_another_month` | Trips from the wrong month are removed |
| `test_returns_the_columns_the_model_needs` | Every feature column is there |

**Walk through `tests/test_api.py`:** it trains a tiny model on made-up trips, so it needs no MLflow server and no data download.

| Test | Checks that |
|---|---|
| `test_health` | `/health` answers |
| `test_predict_returns_minutes` | `/predict` returns a positive number |
| `test_api_fields_match_model_features` | The API fields match the model's features, in order |
| `test_rejects_unknown_zone` | Zone `999` gets a `422` |
| `test_rejects_missing_field` | A missing field gets a `422` |
| `test_rejects_wrong_hour` | Hour `24` gets a `422` |

**Point out:** tests should be fast and need nothing outside the repo. That's why they use made-up data.

## Part 3: The model check (15 min)

```
python src/download_data.py 2019-10 2019-11
python src/check_model.py
```

Expected: error 3.32, `PASSED`.

**Explain:** `check_model.py` trains with our current code on October 2019 and tests on November 2019. If the error is above 3.6 minutes, it exits with code 1, and a non-zero exit code makes a CI job fail.

**Why 3.6?** Our model scores about 3.3, so 3.6 allows some room before it fails. Measured on this data:

| Change | Error | Result |
|---|---|---|
| Our current code | 3.32 | ✅ |
| Train on 20,000 rows | 3.45 | ✅ |
| Train on 2,000 rows | 3.73 | ❌ |
| `max_depth` 5 | 3.77 | ❌ |

**Point out:** after passing, it saves the model to `model/`. CI puts **exactly this checked model** in the Docker image.

## Part 4: Read the workflow (15 min)

Open `.github/workflows/ci.yml` and walk through it top to bottom.

| Part | Meaning |
|---|---|
| `on: push: branches: [main]` and `pull_request` | Run on pushes to `main` and on every PR |
| `runs-on: ubuntu-latest` | Each job gets a fresh Linux machine |
| `uses: actions/checkout@v7` | Copy the repo onto that machine |
| `uses: actions/setup-python@v7` | Install Python, and cache packages for next time |
| `run:` | Run a command, as in a terminal |
| `needs: test` | Wait for `test` to pass first |
| `upload-artifact` / `download-artifact` | Pass the checked model from one job to the next |

**Ask:** "Why does each job need its own `checkout` and `setup-python`?"
**Answer:** every job starts on a brand-new machine with nothing on it.

**Ask:** "Why not build the Docker image first?"
**Answer:** there's no point building an image for code that fails its tests, or a model that fails its check.

## Part 5: Push and get green (15 min)

Follow README Step 4. Then open the **Actions** tab together and click into the run. Show:
- The three jobs and the arrows between them
- The log for each step
- The `model` artifact saved on the run page

## Part 6: Break it on purpose (25 min)

### Demo A: a code bug

Change `between(1, 60)` to `between(0, 60)` in `src/common.py` and open a PR (README Step 6).

| Job | Result |
|---|---|
| `test` | ❌ `test_removes_a_trip_under_one_minute` fails |
| `model-check` | Skipped |
| `docker` | Skipped |

**Show:** click the failed job and read the error together. Students should learn to find the failing line in a CI log.

### Demo B: a weak model

Change `MAX_TRAIN_ROWS = 100_000` to `MAX_TRAIN_ROWS = 2_000` and open a PR (README Step 7). The story is a teammate trying to make training faster.

| Job | Result |
|---|---|
| `test` | ✅ All 13 pass |
| `model-check` | ❌ Error 3.73, above the 3.6 limit |
| `docker` | Skipped |

**This is the key lesson of the class:** the code is correct, so every test passes, but the model got worse. Normal software CI would let this through, and ML CI needs a model check too.

Fix both PRs by reverting the change and pushing again, and show them turn green.

## Part 7: Block bad merges (10 min)

Set up a ruleset on `main` that requires `test`, `model-check` and `docker` to pass (README Step 8). Then open a red PR again and show that the **Merge** button is blocked.

**Note:** this may not be enforced on private repos with a free plan, which is why students use public repos. Check it on your test repo before class.

---

## Check understanding

1. **What starts the workflow?** A push to `main`, or any pull request.
2. **Why did demo B pass the tests but fail CI?** The code was correct, but the model was worse. Tests check code, and the model check checks the model.
3. **What does `needs` do?** It makes a job wait for another job to pass.
4. **Why do the API tests use a made-up model?** So they run fast without MLflow or data downloads.
5. **How does a script make a CI job fail?** It exits with a non-zero code, such as `sys.exit(1)`.
6. **Which model goes into the CI Docker image?** The exact model that passed `check_model.py`, passed between jobs as an artifact.

## Likely student questions

- **Is this model the champion from MLflow?** No. CI has no MLflow server, so it trains its own model to check the code. The image it builds is a test that the image works. Shipping the real champion stays as in Class 3.
- **Does CI cost money?** GitHub Actions is free for public repos on standard machines. Private repos get a limited number of free minutes each month.
- **Why train on one month only?** It keeps CI quick. The full training still happens with `train.py`.
- **Why `pull_request` and not every push?** We still run on pushes to `main`. Checking PRs catches problems before they reach `main`.

## Homework

1. Add a test that removes trips with a negative `trip_distance`.
2. Add a CI status badge to the README.
3. **Bonus:** add a scheduled workflow (`on: schedule`) that runs `monitor.py` every week.

## Next class

The course roadmap still includes data versioning (DVC) and continuous deployment, such as pushing the image to a registry automatically on `main`.
