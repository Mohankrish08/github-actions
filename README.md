# Class 4: GitHub Actions, ovvoru push um automatic ah check aagum

Class 3 la ella checks um naama kaila run pannom. Indha class la GitHub Actions adha automatic ah pannum. Code push pannina odane GitHub moonu checks run pannum:

```
push / pull request ──► 1. Tests ──► 2. Model check ──► 3. Docker build ──► ✅ merge pannalam
                           ❌              ❌                  ❌
                       code bug       weak model         image broken
```

Same taxi project dhaan. Pudhusa vandhadhu tests, model check, matrum workflow mattum dhaan.

## Pudhu files

| File | Velai |
|---|---|
| `tests/test_data.py` | `load_month` bad trips ah remove pannudha nu check pannum |
| `tests/test_api.py` | `/health`, `/predict`, matrum thappana input ku `422` varudha nu check pannum |
| `src/check_model.py` | Model ah train panni, error 3.6 nimisham ku mela pona fail aagum |
| `.github/workflows/ci.yml` | GitHub la run aagura moonu jobs |

Class 3 files maaradhu, rendu sinna changes mattum:
- `common.py`: `MLFLOW_TRACKING_URI` environment variable irundha adha use pannum.
- `download_data.py`: ippo months ah mattum kuduthu download pannalam, e.g. `2019-10 2019-11`.

## Enna venum

- Python 3.10 or above
- Git installed (`git --version` run panni check pannunga)
- GitHub account

Ella commands um `taxi-class-4` folder kulla irundhu dhaan run pannanum.

## Step 1: Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install ".[test]"
```

## Step 2: Tests ah laptop la run pannunga

```
pytest -v
```

Expected: `13 passed`. Indha tests ku MLflow server um venda, data um venda.

## Step 3: Model check ah laptop la run pannunga

```
python src/download_data.py 2019-10 2019-11
python src/check_model.py
```

Expected:

```
Trained on 2019-10, tested on 2019-11: error 3.32 minutes (limit 3.6)
PASSED: saved the model to model/ as version ci-local
```

## Step 4: GitHub ku push pannunga

1. GitHub la pudhu **public** repo create pannunga, e.g. `taxi-mlops`. README add pannadheenga, empty ah irukkanum.
2. Indha commands run pannunga. `YOUR-NAME` ku badhila unga GitHub username podunga:

```
git init -b main
git add .
git commit -m "Taxi project with CI"
git remote add origin https://github.com/YOUR-NAME/taxi-mlops.git
git push -u origin main
```

First time push pannumbodhu browser la GitHub login kekkum.

`.gitignore` irukkuradhala `data/`, `model/`, `mlflow.db` ellam GitHub ku pogadhu.

## Step 5: Green ✅ ah paarunga

GitHub la unga repo open panni **Actions** tab ku ponga. **CI** workflow la moonu jobs varisaiya run aagum:

| Job | Enna pannum |
|---|---|
| `test` | `pytest` run pannum |
| `model-check` | 2 months data download panni, model ah check pannum, model ah save pannum |
| `docker` | Andha model vechu image build panni, API ah start panni, oru prediction try pannum |

Moonum green aana, unga code safe.

## Step 6: Vendumnu break pannunga, demo A (code bug)

```
git switch -c demo-a
```

`src/common.py` la `between(1, 60)` ah `between(0, 60)` nu maathunga. Apram:

```
git commit -am "Allow 0-minute trips"
git push -u origin demo-a
```

GitHub la **Compare & pull request** click panni PR open pannunga. Expected: `test` ❌ fail aagum, `test_removes_a_trip_under_one_minute` red la varum. `model-check` and `docker` skip aagum.

Fix panna `between(1, 60)` nu thirumba maathi, commit panni, push pannunga. ✅ green aagum.

## Step 7: Demo B (weak model)

```
git switch main
git switch -c demo-b
```

`src/common.py` la `MAX_TRAIN_ROWS = 100_000` ah `MAX_TRAIN_ROWS = 2_000` nu maathunga ("training fast aagum" nu solli). Apram:

```
git commit -am "Train on fewer rows to go faster"
git push -u origin demo-b
```

PR open pannunga. Expected:
- `test` ✅ pass, code la bug illa
- `model-check` ❌ fail, error 3.73, limit 3.6

**Paadam:** code tests pass aanalum model mosama irukkalam. Adhunaala dhaan model ku thani check venum.

## Step 8: Red PR ah merge panna mudiyadha maari pannunga

Repo **Settings** → **Rules** → **Rulesets** → **New branch ruleset**:
1. Target: `main` (Default branch)
2. **Require status checks to pass** tick pannunga
3. `test`, `model-check`, `docker` moonaiyum add pannunga
4. Save

Ippo red PR la **Merge** button block aagum.

Private repo na indha rule work aagama irukkalam, adhunaala dhaan public repo use pannrom.

## Error vandha enna pannanum

| Error | Karanam | Fix |
|---|---|---|
| `pytest` not found | Venv activate aagala, illa `.[test]` install aagala | `.venv\Scripts\activate` apram `pip install ".[test]"` |
| `No such file or directory: data\...` | Model check ku data illa | `python src/download_data.py 2019-10 2019-11` |
| `git push` la `rejected` | GitHub repo empty illa | README illama pudhu repo create pannunga |
| Actions tab la onnum illa | `.github` folder push aagala | `git status` paarunga, `.github/workflows/ci.yml` commit aagirukkanum |
| `model-check` download step fail | GitHub la irundhu data site ah reach panna mudiyala | Job ah **Re-run** pannunga |

## Laptop la full project ah run panna

Class 3 commands ellam inga um work aagum (`train.py`, `monitor.py`, `retrain.py`, `serve.py`). Monitoring ku Evidently venum:

```
pip install ".[monitor]"
```

## Homework

1. `test_data.py` la negative `trip_distance` remove aagudha nu oru test add pannunga.
2. README la CI status badge add pannunga: Actions → CI → `...` → **Create status badge**.
3. **Bonus:** Ovvoru vaaram `monitor.py` run aagura maari oru scheduled workflow (`on: schedule`) ezhudhunga.
