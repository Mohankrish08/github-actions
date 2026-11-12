# Class 5: Continuous Deployment, Render la live API (end-to-end guide)

**Class time:** about 2 hours
**Project:** Class 4 taxi project + automatic deploy to Render (free)

---

## 0. Indha class la enna pannrom?

Class 4 la GitHub Actions namma code ah **check** pannudhu. Aana API eppovum odura URL illa. Postman la call panna mudiyala.

Indha class la, ella checks um pass aana, GitHub Actions ae Docker image ah build panni, **Render** la live aakkum. Apram oru **public URL** kidaikkum. Postman, browser, yaar venumnaalum call pannalam.

```
git push to main
   │
   ▼
GitHub Actions
   1. test ✅ ──► 2. model-check ✅ ──► 3. docker ✅ ──► 4. deploy 🚀   ← NEW
                                                            │
                         image push ──► ghcr.io (GitHub oda image store)
                                                            │
                         "pudhu image ready" ──► Render (eppovum odum)
                                     https://taxi-api-xxxx.onrender.com
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

**Oru line la:** "CI check pannum, CD ship pannum. GitHub Actions gatekeeper, Render server."

### Indha class mudinja appram students ku theriyanum

1. CI um CD um enna difference
2. Rahasiyamaana URL/token ah eppadi safe ah GitHub **secret** ah vekkanum
3. Deploy job eppo run aagum, eppo run aagaadhu
4. Live API ah Postman la call pannuvadhu
5. Pudhu push → pudhu version live aagradhu, adha eppadi confirm pannuvadhu

---

## 1. Mukkiyamaana words

| Word | Simple ah artham |
|---|---|
| **CD** (Continuous Deployment) | Checks pass aana, automatic ah live ku ship pannradhu |
| **Render** | Namma Docker image ah eppovum run panra server. Free plan irukku |
| **ghcr.io** | GitHub Container Registry. GitHub la Docker images vekkura idam. Free |
| **Image tag** | Image oda version name, e.g. `ci-a4f8e21`. Model version um adhe |
| **Deploy hook** | Render kudukkura rahasiya URL. Adha call panna, Render pudhu image ah deploy pannum |
| **GitHub secret** | Rahasiyamaanadha safe ah vekkura idam. Logs la kooda `***` nu dhaan varum |
| **GitHub variable** | Rahasiyam illaadha setting, e.g. live URL |
| **Cold start** | Free Render 15 nimisham use aagala na thoongidum. First request slow ah varum |

> **Yen Hugging Face illa?** Hugging Face ippo Docker Spaces ku PRO (kaasu) kekkudhu (`402 Payment Required`). Render free plan la Docker image run pannalam.

---

## 2. Class 4 la irundhu enna maaruchu?

| File | Change |
|---|---|
| `deploy/deploy_render.py` | **NEW:** Render ku "indha image ah deploy pannu" nu solli, live aagura varaikkum wait panni, test pannum |
| `.github/workflows/ci.yml` | **NEW job `deploy`**, `docker` ku apram |
| `Dockerfile` | App **user 1000** ah run aagum (root illa, safe). Port: Render `$PORT` kudutha adhu, illana 8000 |

Meedhi ellam (tests, model check, predict buttons) Class 4 maari ye.

---

## 3. Part A: Render account (5 min)

https://render.com → **Get Started** → **GitHub** vechu sign up pannunga. Card venaam.

Ippo vera onnum pannaadheenga. Service ah Part D la create pannuvom, image ready aana apram.

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
docker build -t taxi-api .
docker run -d --name api -e PORT=10000 -p 10000:10000 taxi-api
```

`-e PORT=10000` na Render maari port kudukkurom. Browser la: http://localhost:10000/health

```json
{"status":"ok","model_version":"ci-local"}
```

**Explain:** Render namma app ku `PORT` nu oru number kudukkum. Dockerfile la `--port ${PORT:-8000}` irukku: `PORT` irundha adhu, illana 8000. Adhaan CI la 8000, Render la avanga port.

Mudinjadhum: `docker rm -f api`

---

## 5. Part C: `deploy` job ah purinjukkonga (20 min)

`.github/workflows/ci.yml` la keela:

```yaml
  deploy:
    needs: docker
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    concurrency: deploy
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v7
      - uses: actions/download-artifact@v8
        with:
          name: model
          path: model/
      - name: Build the image and push it to GitHub's registry
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          IMAGE="ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/taxi-api"
          VERSION=$(cat model/version.txt)
          echo "$GH_TOKEN" | docker login ghcr.io -u "${{ github.actor }}" --password-stdin
          docker build --provenance=false --sbom=false -t "$IMAGE:$VERSION" -t "$IMAGE:latest" --label "..." .
          docker push --all-tags "$IMAGE"
          echo "IMAGE=$IMAGE:$VERSION" >> "$GITHUB_ENV"
      - run: python3 deploy/deploy_render.py
        env:
          RENDER_DEPLOY_HOOK: ${{ secrets.RENDER_DEPLOY_HOOK }}
          RENDER_URL: ${{ vars.RENDER_URL }}
```

| Line | Artham |
|---|---|
| `needs: docker` | Moonu checks um pass aana dhaan deploy |
| `if: ... 'refs/heads/main'` | `main` ku push panna mattum. **Pull request la deploy aagaadhu**, review aagaadha code live ku pogakoodadhu |
| `concurrency: deploy` | Rendu push vegama vandhaalum, orey time la oru deploy dhaan |
| `permissions: packages: write` | Indha job ku mattum ghcr.io la image push panna permission |
| `download-artifact` | Check pass aana **adhe model** dhaan image kulla pogum |
| `secrets.GITHUB_TOKEN` | GitHub ovvoru run kum automatic ah kudukkura token. Naama create panna thevai illa |
| `${GITHUB_REPOSITORY_OWNER,,}` | Username ah small letters aakkum (`Mohankrish08` → `mohankrish08`). Image name la capital letters koodaadhu |
| `-t "$IMAGE:$VERSION" -t "$IMAGE:latest"` | Orey image ku rendu tags: version name, matrum `latest` |
| `--provenance=false --sbom=false` | Simple image mattum. Extra "attestation" records irundhaa GitHub registry `denied` nu reject pannum |
| `docker push --all-tags` | Rendu tags um ghcr.io ku |
| `GITHUB_ENV` | Image name ah adutha step ku anuppum |
| `secrets.RENDER_DEPLOY_HOOK` | Render hook URL, secret la. Adhu theriyura yaar venumnaalum deploy pannalam, adhunaala secret |
| `vars.RENDER_URL` | Live URL. Rahasiyam illa, variable |

### `deploy_render.py` enna pannudhu (step by step)

```
1. model/version.txt padikkum                      → e.g. ci-a4f8e21
2. Hook / URL set aagala na → setup steps kaatti stop
3. Render hook ah call pannum, "indha tag deploy pannu" → hook + &imgURL=ghcr.io/.../taxi-api:ci-a4f8e21
4. Render image ah pull panni start pannum (sila nimisham)
5. Ovvoru 20 second kum /health check pannum        → pudhu version varra varaikkum (max 15 min)
6. /predict ku oru test trip anuppum
7. Live URL ah GitHub summary page la podum
```

**Class kitta kelunga:** "Hook call aana odane mudinjudhu nu sollalaama?"
**Answer:** "Illa. Render image pull panna fail aagalaam, app start aagaama pogalaam. Live URL pudhu version sollura varaikkum wait panni, test pannina dhaan 'deployed' nu sollanum."

**Kelunga:** "Render yen namma code ah build pannala? Image ah yen GitHub la build pannrom?"
**Answer:** "Model file GitHub repo la illa (`.gitignore`). CI la check pass aana model dhaan image kulla pogum. Test pannina adhe image dhaan live ku pogum."

---

## 6. Part D: First push + one-time Render setup (20 min)

### D1. Push pannunga

```
git add .
git commit -m "Deploy to Render"
git push
```

**Actions** tab la **4 jobs**. Indha first time la `deploy` ❌ aagum. **Adhu expected.** Image push aachu, aana Render service innum illa. Log la:

```
One-time setup is not finished. The image is already pushed: ghcr.io/<you>/taxi-api:ci-xxxxxxx
1. GitHub > your profile > Packages > taxi-api > ...
```

### D2. Image ah public aakkunga

GitHub → unga profile picture → **Your profile** → **Packages** tab → **taxi-api** → **Package settings** (right side keela) → **Danger Zone** → **Change visibility** → **Public**.

Yen? Render password illaama image ah pull panna, image public ah irukkanum. Image la code um model um dhaan irukku, rahasiyam illa.

### D3. Render service create pannunga

1. https://dashboard.render.com → **New** → **Web Service**
2. **Existing Image** select pannunga
3. Image URL: `ghcr.io/<github-username-small-letters>/taxi-api:latest` (e.g. `ghcr.io/mohankrish08/taxi-api:latest`) → **Connect**
4. Name: `taxi-api`
5. Region: **Singapore** (India ku pakkam)
6. Instance Type: **Free**
7. **Deploy Web Service**

Top la unga URL varum, e.g. `https://taxi-api-xxxx.onrender.com`. Copy pannunga. Sila nimishathula **Live** nu varum.

### D4. Deploy hook copy pannunga

Render service → **Settings** → **Deploy Hook** → URL copy pannunga.

⚠️ **Hook URL ah code la, chat la, screenshot la podaadheenga.** Adhu theriyura yaar venumnaalum unga service ah deploy pannalam.

### D5. GitHub la secret and variable

Repo → **Settings** → **Secrets and variables** → **Actions**

| Tab | Name | Value |
|---|---|---|
| **Secrets** → New repository secret | `RENDER_DEPLOY_HOOK` | D4 hook URL |
| **Variables** → New repository variable | `RENDER_URL` | D3 URL, e.g. `https://taxi-api-xxxx.onrender.com` (kadaisi la `/` venaam) |

### D6. Re-run

Failed run page → **Re-run jobs** → **Re-run failed jobs**. `deploy` step la:

```
Deploying model ci-xxxxxxx as ghcr.io/<you>/taxi-api:ci-xxxxxxx
Render accepted the deploy (HTTP 200)
live version: ci-yyyyyyy
live version: not answering yet
...
live version: ci-xxxxxxx
LIVE: https://taxi-api-xxxx.onrender.com/predict answered {'minutes': 16.2, 'model_version': 'ci-xxxxxxx'}
```

Run summary la **🚀 Deployed model** table: live URL, `/docs` link, Postman URL.

Render la um paakkalam: service page → **Events** (deploys) and **Logs** (app output).

Idhu ellam **orey thadava** dhaan. Ini push pannina automatic.

---

## 7. Part E: Live inference (25 min)

### Browser

`https://taxi-api-xxxx.onrender.com/docs` → **POST /predict** → **Try it out** → JSON paste → **Execute**

### Postman

1. **New** → **HTTP**
2. Method: **POST**
3. URL: `https://taxi-api-xxxx.onrender.com/predict`
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
Invoke-RestMethod -Method Post -Uri https://taxi-api-xxxx.onrender.com/predict -ContentType "application/json" -Body '{"PULocationID":74,"DOLocationID":75,"trip_distance":2.5,"hour":8,"weekday":1}'
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

⚠️ **First request slow ah irundhaa (~1 nimisham):** free Render 15 nimisham use aagala na thoongidum (cold start). Class ku 10 nimisham munnadi `/health` open panni ezhuppunga.

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

**Sollunga:** "Naama Render website ah touch kooda pannala. Push mattum dhaan. Check pass aachu, adhuve ship aachu."

### Bad change live ku pogumaa?

Illa. Class 4 la paatha maari, test fail aanaalum, model mosam aanaalum (`model-check` ❌), `deploy` **skip aagum**. Live API pazhaya nalla version laye irukkum.

| Push | test | model-check | docker | deploy | Live API |
|---|---|---|---|---|---|
| Nalla change | ✅ | ✅ | ✅ | ✅ | Pudhu version |
| Code bug | ❌ | skip | skip | skip | **Pazhaya version** (safe) |
| Weak model (3.73) | ✅ | ❌ | skip | skip | **Pazhaya version** (safe) |
| Pull request | ✅ | ✅ | ✅ | skip | Maaradhu (merge aana apram dhaan) |

### Rollback

Pudhu version la problem na, pazhaya green run ah thirumba deploy pannalam: **Actions** → **CI** → pazhaya green run → **Re-run all jobs**. Adhu andha commit oda code ah thirumba check panni deploy pannum. Render la um **Events** → pazhaya deploy → **Rollback** button irukku. (Rendu um class la try pannala, practice la oru thadava try pannunga.)

---

## 9. Error vandha enna pannanum

| Error (deploy job la) | Karanam | Fix |
|---|---|---|
| `One-time setup is not finished` | Hook secret illa URL variable add pannala | Part D2 to D6 |
| `denied` in docker push | Job ku packages permission illa, illa build la attestation records | `permissions: packages: write` and `--provenance=false --sbom=false` irukkaa paarunga |
| `Render refused the deploy (HTTP 404)` | Hook thappu, illa Render service image name vera | Hook ah thirumba copy pannunga. Service image `ghcr.io/<you>/taxi-api:latest` ah irukkanum |
| `was not live after 15 minutes` | Render image pull panna mudiyala, illa app start aagala | Render service → **Events** / **Logs**. Image **public** ah irukkaa (D2) paarunga |
| `deploy` job skip aagudhu | Pull request, illa `main` illaadha branch | Normal dhaan. `main` ku merge/push pannunga |
| Postman la timeout / 502 | Render thoongudhu (cold start) | 1 nimisham wait panni retry |
| Postman la `422` | JSON la thappu value illa field missing | Response la endha field nu sollum |

---

## 10. Check understanding

1. **CI um CD um enna difference?** CI check pannum. CD, check pass aana, automatic ah ship pannum.
2. **Hook URL ah yen code la podakoodadhu?** GitHub la yaar paathaalum unga service ah deploy pannalam. Secret la vechaa logs la kooda theriyaadhu.
3. **Pull request la deploy aagumaa?** Illa. `main` ku push panna mattum. Review aagaadha code live ku pogakoodadhu.
4. **Weak model push panna live API ku enna aagum?** Onnum aagaadhu. `model-check` fail, `deploy` skip, pazhaya version laye irukkum.
5. **Hook call aana odane "deployed" nu sollalaama?** Illa. Live URL pudhu version sollura varaikkum wait panni test pannanum.
6. **Live API la endha version odudhu nu eppadi theriyum?** `/health` illa `/predict` answer la `model_version`.
7. **First request yen slow?** Free Render thoongidum (cold start).

## 11. Homework

1. Postman la oru **Collection** create panni, Part E la irukkura 5 tries um save pannunga.
2. `serve.py` la oru pudhu endpoint add pannunga: `GET /version` → `{"model_version": ...}`. Push panni live la check pannunga.
3. `deploy_render.py` la test trip ku badhila `samples/trips.csv` la irukkura 3 trips ah live API ku anuppi, summary la table podunga.
4. **Bonus:** Render free plan limits padinga: sleep, monthly hours, RAM. Namma app evlo RAM use pannudhu? (Laptop la ~215 MB)

## 12. Class 4 features inga um irukku

`Predict a trip` and `Predict sample trips` buttons, `pytest`, `check_model.py`, Class 3 commands (`train.py`, `monitor.py`, `retrain.py`) ellam inga um work aagum.
