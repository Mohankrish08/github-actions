# Class 5: Continuous Deployment, Hugging Face la live API (end-to-end guide)

**Class time:** about 2 hours
**Project:** Class 4 taxi project + automatic deploy to a Hugging Face Space

---

## 0. Indha class la enna pannrom?

Class 4 la GitHub Actions namma code ah **check** pannudhu. Aana API eppovum odura URL illa. Postman la call panna mudiyala.

Indha class la, ella checks um pass aana, GitHub Actions ae model ah **Hugging Face Space** ku deploy pannum. Apram oru **public URL** kidaikkum. Postman, browser, yaar venumnaalum call pannalam.

```
git push to main
   │
   ▼
GitHub Actions
   1. test ✅ ──► 2. model-check ✅ ──► 3. docker ✅ ──► 4. deploy 🚀   ← NEW
                                                            │
                                                            ▼
                                     Hugging Face Space (eppovum odum)
                                     https://<hf-username>-taxi-api.hf.space
                                        ├── GET  /health
                                        ├── POST /predict   ◄── Postman
                                        └── GET  /docs      ◄── browser
```

| | Class 4 (CI) | Class 5 (CD) |
|---|---|---|
| Enna pannudhu | Check pannum | Check panni, **ship** pannum |
| API | Job mudinjadhum azhinjidum | Eppovum odum, public URL |
| Postman | ❌ | ✅ |
| Pudhu model users kitta | Kaila deploy pannanum | Green aana odane automatic |

**Oru line la:** "CI check pannum, CD ship pannum. GitHub Actions gatekeeper, Hugging Face server."

### Indha class mudinja appram students ku theriyanum

1. CI um CD um enna difference
2. Token ah eppadi safe ah GitHub **secret** ah vekkanum
3. Deploy job eppo run aagum, eppo run aagaadhu
4. Live API ah Postman la call pannuvadhu
5. Pudhu push → pudhu version live aagradhu, adha eppadi confirm pannuvadhu

---

## 1. Mukkiyamaana words

| Word | Simple ah artham |
|---|---|
| **CD** (Continuous Deployment) | Checks pass aana, automatic ah live ku ship pannradhu |
| **Hugging Face Space** | Hugging Face la free ah app run panna oru idam. Namma Docker image ah run pannum |
| **Access token** | Password maari oru key. Adhu vechu dhaan GitHub, Hugging Face la upload pannum |
| **GitHub secret** | Token maari rahasiyam ah vekka vendiyadha safe ah store panra idam. Logs la kooda theriyaadhu |
| **GitHub variable** | Rahasiyam illaadha setting, e.g. Space name |
| **Cold start** | Free Space konja neram use aagala na thoongidum. First request slow ah varum |

---

## 2. Class 4 la irundhu enna maaruchu?

| File | Change |
|---|---|
| `deploy/deploy_space.py` | **NEW:** files ah prepare panni, Space ku upload panni, live aagura varaikkum wait panni, test pannum |
| `.github/workflows/ci.yml` | **NEW job `deploy`**, `docker` ku apram |
| `Dockerfile` | App ippo **user 1000** ah run aagum, root ah illa. Hugging Face apdi dhaan run pannum, so CI um adhe maari test pannum |

Meedhi ellam (tests, model check, predict buttons) Class 4 maari ye.

---

## 3. Part A: One-time setup (15 min)

### Step A1: Hugging Face account

https://huggingface.co la free account create pannunga. Unga **username** note pannunga.

### Step A2: Write token create pannunga

1. huggingface.co → right top la profile picture → **Settings** → **Access Tokens**
2. **Create new token**
3. Token type: **Write**
4. Name: `github-deploy`
5. **Create token** → token ah copy pannunga (`hf_...` nu aarambikkum)

⚠️ **Token ah code la, chat la, screenshot la eppovum podaadheenga.** Yaaru kitta irundhaalum avanga unga account la upload pannalam.

### Step A3: GitHub la secret and variable add pannunga

Unga GitHub repo → **Settings** → **Secrets and variables** → **Actions**

**Secret** (Secrets tab → **New repository secret**):

| Name | Value |
|---|---|
| `HF_TOKEN` | Step A2 la copy panna token |

**Variable** (Variables tab → **New repository variable**):

| Name | Value |
|---|---|
| `HF_SPACE` | `<hf-username>/taxi-api` (e.g. `mohan/taxi-api`) |

Space ah neenga create panna thevai illa. First deploy la script ae create pannum.

**Sollunga:** "Secret na save pannina apram GitHub kooda adha thirumba kaattaadhu. Logs la `***` nu dhaan varum."

---

## 4. Part B: Laptop la check pannunga (15 min)

```
python -m venv .venv
.venv\Scripts\activate
pip install ".[test]"
pytest -v
```

Expected: `13 passed`.

```
python src/download_data.py 2019-10 2019-11
python src/check_model.py
python deploy/deploy_space.py --dry-run
```

`--dry-run` upload pannaadhu. Space ku enna files pogum nu mattum kaattum:

```
Prepared version ci-local in ...:
   Dockerfile
   model/MLmodel
   model/model.skops
   ...
   pyproject.toml
   README.md
   src/serve.py
   ...
```

**Explain:** `README.md` ah script ae create pannum. Adhoda top la irukkura settings Hugging Face ku sollum:

```yaml
sdk: docker      # Dockerfile vechu build pannu
app_port: 8000   # namma API port 8000 la odum
```

---

## 5. Part C: `deploy` job ah purinjukkonga (20 min)

`.github/workflows/ci.yml` la keela:

```yaml
  deploy:
    needs: docker
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    concurrency: deploy
    steps:
      - uses: actions/checkout@v7
      - uses: actions/download-artifact@v8
        with:
          name: model
          path: model/
      - uses: actions/setup-python@v7
        with:
          python-version: "3.10"
      - run: pip install "huggingface_hub==2.4.0"
      - run: python deploy/deploy_space.py
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
          HF_SPACE: ${{ vars.HF_SPACE }}
```

| Line | Artham |
|---|---|
| `needs: docker` | Moonu checks um pass aana dhaan deploy |
| `if: ... 'refs/heads/main'` | `main` ku push panna mattum. **Pull request la deploy aagaadhu**, review aagaadha code live ku pogakoodadhu |
| `concurrency: deploy` | Rendu push vegama vandhaalum, orey time la oru deploy dhaan |
| `download-artifact` | Check pass aana **adhe model** dhaan live ku pogum |
| `huggingface_hub` | Hugging Face oda Python library, upload panna |
| `secrets.HF_TOKEN` | Secret la irundhu token. Code la illa |
| `vars.HF_SPACE` | Variable la irundhu Space name |

### `deploy_space.py` enna pannudhu (step by step)

```
1. model/version.txt padikkum                       → e.g. ci-088a267
2. Dockerfile, pyproject.toml, src/, model/ copy     → oru pudhu folder la
   + Space README.md (sdk: docker, app_port: 8000)
3. Space illa na create pannum                       → create_repo(..., exist_ok=True)
4. Ella files um upload                              → upload_folder(...)
5. Hugging Face image build pannum (sila nimisham)
6. Ovvoru 20 second kum /health check pannum         → pudhu version varra varaikkum
   Build fail aana odane stop, logs link kaattum
7. /predict ku oru test trip anuppum
8. Live URL ah GitHub summary page la podum
```

**Class kitta kelunga:** "Upload aana odane mudinjudhu nu sollalaama?"
**Answer:** "Illa. Upload aanaalum build fail aagalaam. Live URL pudhu version sollura varaikkum wait panni, test pannina dhaan 'deployed' nu sollanum."

**Kelunga:** "Yen `git push` vechu Hugging Face ku anuppala?"
**Answer:** "Model file 23 MB. Hugging Face git push periya files ah thadukkum (Git LFS venum). `huggingface_hub` library adha automatic ah handle pannum."

---

## 6. Part D: Push panni deploy aagradha paarunga (15 min)

Unga repo la (Class 4 repo, illa pudhu repo) indha folder files ah vechu:

```
git add .
git commit -m "Deploy to Hugging Face"
git push
```

**Actions** tab la ippo **4 jobs**:

```
test ──► model-check ──► docker ──► deploy
```

`deploy` job la **Run python deploy/deploy_space.py** step ah expand pannunga:

```
Prepared version ci-xxxxxxx in ...
Uploaded to https://huggingface.co/spaces/<you>/taxi-api. Waiting for https://<you>-taxi-api.hf.space ...
Space: BUILDING         live version: not answering yet
Space: BUILDING         live version: not answering yet
...
Space: RUNNING          live version: ci-xxxxxxx
LIVE: https://<you>-taxi-api.hf.space/predict answered {'minutes': ..., 'model_version': 'ci-xxxxxxx'}
```

Run page summary la **🚀 Deployed model** table varum: live URL, `/docs` link, Postman URL.

Hugging Face la um paakkalam: `https://huggingface.co/spaces/<you>/taxi-api` → **Logs** tab la build nadakkuradhu theriyum.

---

## 7. Part E: Live inference (25 min)

### Browser

`https://<you>-taxi-api.hf.space/docs` → **POST /predict** → **Try it out** → JSON paste → **Execute**

### Postman

1. **New** → **HTTP**
2. Method: **POST**
3. URL: `https://<you>-taxi-api.hf.space/predict`
4. **Body** → **raw** → **JSON**
5. Paste:
   ```json
   {"PULocationID": 74, "DOLocationID": 75, "trip_distance": 2.5, "hour": 8, "weekday": 1}
   ```
6. **Send**

Answer:

```json
{"minutes": 16.2, "model_version": "ci-xxxxxxx"}
```

`16.2` laptop la same code vechu vandha number.

### PowerShell (Postman illa na)

```
Invoke-RestMethod -Method Post -Uri https://<you>-taxi-api.hf.space/predict -ContentType "application/json" -Body '{"PULocationID":74,"DOLocationID":75,"trip_distance":2.5,"hour":8,"weekday":1}'
```

### Class la try pannunga

| Try | Change | Kelunga |
|---|---|---|
| 1 | `trip_distance` 2.5 → 8 | "Neelamaana trip, adhigam nimisham?" (laptop la 32.9) |
| 2 | `hour` 8 → 3 | "Kaalai 3 mani, roads empty, fast?" (laptop la 9.2) |
| 3 | `weekday` 1 → 6 | "Sunday, office traffic illa?" (laptop la 11.6) |
| 4 | `PULocationID` → 999 | "Thappana zone?" → **422** error |
| 5 | `trip_distance` remove pannunga | "Field missing?" → **422** error |

**Sollunga:** "Ippo idhu oru real API. Unga phone la irundhu kooda call pannalam. Mobile app, website, yaar venumnaalum use pannalam."

⚠️ **First request slow ah irundhaa:** free Space thoongittu irukkum (cold start). Konja neram wait panni thirumba try pannunga. Class ku munnadi `/health` open panni Space ah ezhuppunga.

---

## 8. Part F: Pudhu version ship pannunga (15 min)

CD oda power idhu dhaan. Oru change push pannunga, automatic ah live aagum.

1. Edhaavadhu sinna change pannunga, e.g. `src/serve.py` la `title="Taxi trip duration API"` ah `title="Taxi trip duration API v2"` nu.
2. Push:
   ```
   git commit -am "API v2"
   git push
   ```
3. 4 jobs um green aagura varaikkum wait pannunga.
4. Postman la **Send** thirumba click pannunga. `model_version` pudhu commit ID ah maari irukkum.
5. `/docs` refresh pannunga. Title la "v2" varum.

**Sollunga:** "Naama Hugging Face website ah touch kooda pannala. Push mattum dhaan. Check pass aachu, adhuve ship aachu."

### Bad change live ku pogumaa?

Illa. Class 4 la paatha maari, test fail aanaalum, model mosam aanaalum (`model-check` ❌), `deploy` **skip aagum**. Live API pazhaya nalla version laye irukkum.

| Push | test | model-check | docker | deploy | Live API |
|---|---|---|---|---|---|
| Nalla change | ✅ | ✅ | ✅ | ✅ | Pudhu version |
| Code bug | ❌ | skip | skip | skip | **Pazhaya version** (safe) |
| Weak model (3.73) | ✅ | ❌ | skip | skip | **Pazhaya version** (safe) |
| Pull request | ✅ | ✅ | ✅ | skip | Maaradhu (merge aana apram dhaan) |

### Rollback

Pudhu version la problem na, pazhaya green run ah thirumba deploy pannalam: **Actions** → **CI** → pazhaya green run → **Re-run all jobs**. Adhu andha commit oda code ah thirumba check panni deploy pannum. (Idhu class la try pannala, practice la oru thadava try pannunga.)

---

## 9. Error vandha enna pannanum

| Error (deploy job la) | Karanam | Fix |
|---|---|---|
| `Set HF_TOKEN and HF_SPACE first` | Secret illa variable add pannala | Part A Step A3 |
| `401` / `403` / `Unauthorized` | Token thappu, illa **Read** token | **Write** token create panni secret update pannunga |
| `FAILED: the Space stopped with BUILD_ERROR` | Hugging Face la image build fail | Error la irukkura logs link open pannunga |
| `FAILED: the Space stopped with RUNTIME_ERROR` | Image build aachu, aana API start aagala | Space **Logs** tab paarunga |
| `was not live after 20 minutes` | Build romba slow, illa Space stuck | Space page la status paarunga, **Re-run jobs** |
| `deploy` job skip aagudhu | Pull request, illa `main` illaadha branch | Normal dhaan. `main` ku merge/push pannunga |
| Postman la timeout / 503 | Space thoongudhu (cold start) | Konja neram wait panni retry |
| Postman la `422` | JSON la thappu value illa field missing | Response la endha field nu sollum |

---

## 10. Check understanding

1. **CI um CD um enna difference?** CI check pannum. CD, check pass aana, automatic ah ship pannum.
2. **Token ah yen code la podakoodadhu?** GitHub la yaar paathaalum unga account la upload pannalam. Secret la vechaa logs la kooda theriyaadhu.
3. **Pull request la deploy aagumaa?** Illa. `main` ku push panna mattum. Review aagaadha code live ku pogakoodadhu.
4. **Weak model push panna live API ku enna aagum?** Onnum aagaadhu. `model-check` fail, `deploy` skip, pazhaya version laye irukkum.
5. **Upload aana odane "deployed" nu sollalaama?** Illa. Live URL pudhu version sollura varaikkum wait panni test pannanum.
6. **Live API la endha version odudhu nu eppadi theriyum?** `/health` illa `/predict` answer la `model_version`.
7. **First request yen slow?** Free Space thoongidum (cold start).

## 11. Homework

1. Postman la oru **Collection** create panni, Part E la irukkura 5 tries um save pannunga.
2. `serve.py` la oru pudhu endpoint add pannunga: `GET /version` → `{"model_version": ...}`. Push panni live la check pannunga.
3. `deploy_space.py` la test trip ku badhila `samples/trips.csv` la irukkura 3 trips ah live API ku anuppi, summary la table podunga.
4. **Bonus:** Space settings la hardware, sleep time paarunga. Free tier la enna limits?

## 12. Class 4 features inga um irukku

`Predict a trip` and `Predict sample trips` buttons, `pytest`, `check_model.py`, Class 3 commands (`train.py`, `monitor.py`, `retrain.py`) ellam inga um work aagum.
