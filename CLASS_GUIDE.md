# Class 5 Teaching Guide: Continuous Deployment to a Live API

**Time:** about 2 hours
**Project:** the Class 4 taxi project, plus an automatic deploy to Render (free plan)

How to use this guide: **instructions for you are in English**. Lines marked **🗣 Sollunga** are what to say to students, in Thanglish. Commands and expected output are in `README.md`, and the Part letters match.

## By the end of class, students can

1. Explain the difference between CI and CD
2. Store a secret URL safely as a GitHub secret
3. Say when the deploy job runs and when it doesn't
4. Call the live API from Postman and the browser
5. Ship a new version with a push, and confirm it's live

**🗣 Sollunga:** "Class 4 la GitHub check pannudhu, aana Postman la call panna mudiyala. Indha class mudiyumbodhu, unga model oru real public URL la odum. Push pannina pudhu version automatic ah live aagum."

## Before class

**You**
- [ ] Do the full flow once on your own repo: first push, package public, Render service, hook secret, URL variable, re-run, 4 green jobs
- [ ] Note how long the `deploy` job takes. **It has not run against real Render yet**, only against a local container and a fake hook
- [ ] Open the service's `/health` 10 minutes before class, so it isn't asleep
- [ ] Set up a Postman request for `/predict`
- [ ] Optional: try the rollback (Part F) once

**Students**
- [ ] A Render account (free, sign up with GitHub, no card)
- [ ] Postman installed, or use the browser `/docs` page
- [ ] Their Class 4 repo, with CI green

**Decision for you:** one Render service per student, or one shared service that only you deploy? For a first class, one shared service is simpler: you deploy, everyone calls your URL.

**Why not Hugging Face:** Hugging Face now needs a paid PRO plan to create Docker Spaces (the deploy failed with `402 Payment Required`). If a student asks, that's the answer.

## Class plan

| Time | Part (README) | Outcome |
|---|---|---|
| 10 min | 0–1. CI vs CD | Students know what's new |
| 5 min | A. Render account | Everyone signed in |
| 15 min | B. Laptop check | Image runs with Render's `$PORT` |
| 20 min | C. Read the `deploy` job | `needs`, `if`, `permissions`, secrets |
| 20 min | D. First push and one-time setup | Render service live, 4 green jobs |
| 25 min | E. Live inference | Postman and `/docs` calls, `422` errors |
| 15 min | F. Ship a new version | New `model_version` appears live |
| 5 min | Wrap-up | Check understanding |

---

## Part 0–1: CI vs CD (10 min)

Draw the diagram from README Part 0.

**🗣 Sollunga:** "CI na check pannradhu. CD na, check pass aana, automatic ah ship pannradhu. GitHub Actions gatekeeper maari, nalla model ah mattum ulla vidum. Render server maari, eppovum odum, users ku answer pannum."

**Ask:** "Class 4 la Postman la yen call panna mudiyala?"
**🗣 Answer:** "GitHub Actions machine job mudinjadhum azhinjidum. Server illa. Adhunaala dhaan deploy venum."

## Part A: Render account (5 min)

Everyone signs up with GitHub. Nothing else yet.

## Part B: Laptop check (15 min)

Run `pytest -v`, `check_model.py`, then the Docker run with `-e PORT=10000` from README Part B.

**🗣 Sollunga:** "Render namma app ku 'indha port la odu' nu `PORT` nu oru number kudukkum. Dockerfile la `${PORT:-8000}` irukku: PORT irundha adhu, illana 8000. Laptop la PORT kuduthu test pannrom, Render la um adhe maari work aagum."

**Point out:** the app runs as user 1000, not root.

**🗣 Sollunga:** "Server la app ah root ah run panna koodaadhu. Hack aanaa full machine um poyidum. Normal user ah run pannrom."

## Part C: Read the `deploy` job (20 min)

Use the table in README Part C.

| Line | 🗣 Sollunga |
|---|---|
| `needs: docker` | "Moonu checks um pass aana dhaan deploy." |
| `if: ... refs/heads/main` | "`main` ku push panna mattum. Pull request la deploy aagaadhu. Review aagaadha code live ku pogakoodadhu." |
| `concurrency: deploy` | "Rendu push vegama vandhaalum, orey time la oru deploy dhaan." |
| `permissions: packages: write` | "Indha job ku mattum image push panna anumadhi. Matha jobs ku illa." |
| `download-artifact` | "Check pass aana adhe model dhaan image kulla pogum. Pudhusa train pannala." |
| `secrets.GITHUB_TOKEN` | "GitHub ae ovvoru run kum kudukkura token. Naama edhuvum create pannala." |
| `secrets.RENDER_DEPLOY_HOOK` | "Hook URL theriyura yaar venumnaalum deploy pannalam. Adhunaala secret." |

Then walk through the 7 steps of `deploy_render.py`.

**Ask:** "Hook call aana odane 'deployed' nu sollalaama?"
**🗣 Answer:** "Illa. Render la image pull fail aagalaam, app start aagaama pogalaam. Live URL pudhu version sollura varaikkum wait panni, oru prediction test pannina apram dhaan 'live' nu sollanum. Adhaan script pannudhu."

## Part D: First push and one-time setup (20 min)

Push. The first `deploy` **fails on purpose** with "One-time setup is not finished".

**🗣 Sollunga:** "Red aachu, bayapadaadheenga. Image ready, aana Render ku innum theriyaadhu. Log la ae enna pannanum nu steps irukku."

Do D2 to D6 on the projector: package public, create the Render service from the image, copy the hook, add the secret and variable, re-run.

**🗣 Sollunga:** "Idhu orey thadava dhaan. Ini mel push mattum pannina podhum."

While it deploys, show the service's **Events** and **Logs** on Render.

## Part E: Live inference (25 min)

Open `/docs` in the browser first, then Postman. Use the tries table in README Part E. Ask before each **Send**.

**🗣 Sollunga:** "Ippo idhu real API. Unga phone la irundhu kooda call pannalam. Oru mobile app, website, yaar venumnaalum indha URL ah use pannalam."

Show the `422` errors.

**🗣 Sollunga:** "Thappana input ku model kitta poga koodaadhu. API ae reject pannum. Endha field thappu nu kooda sollum."

If the first call is slow:

**🗣 Sollunga:** "Free Render 15 nimisham use aagala na thoongidum. Idhu cold start. Paid plan la idhu varaadhu."

## Part F: Ship a new version (15 min)

Change the API title to "v2", push, wait for green, then press **Send** in Postman again.

**🗣 Sollunga:** "Naama Render website ah touch kooda pannala. Push mattum dhaan. Check pass aachu, adhuve ship aachu. Idhu dhaan CD."

Then explain why a bad change can't go live, using the table in README Part F.

**🗣 Sollunga:** "Weak model push pannaalum, `model-check` fail aagum, `deploy` skip aagum. Live API pazhaya nalla version laye irukkum. Users ku mosamaana model pogave pogaadhu."

---

## Check understanding

| Question | 🗣 Answer |
|---|---|
| CI um CD um enna difference? | CI check pannum. CD, pass aana, automatic ah ship pannum |
| Hook URL ah yen code la podakoodadhu? | Yaar paathaalum unga service ah deploy pannalam. Secret la vechaa logs la kooda theriyaadhu |
| Pull request la deploy aagumaa? | Illa. `main` ku push panna mattum |
| Weak model push panna live API ku enna aagum? | Onnum aagaadhu. `deploy` skip, pazhaya version laye irukkum |
| Hook call aana odane "deployed" nu sollalaama? | Illa. Live URL pudhu version sollura varaikkum wait panni test pannanum |
| Live la endha version odudhu nu eppadi theriyum? | `/health` illa `/predict` la `model_version` |
| First request yen slow? | Free Render thoongidum, cold start |

## Likely student questions

| Question | 🗣 Answer |
|---|---|
| Render free ah? | "Free plan irukku, card venaam. Aana 15 nimisham use aagala na thoongidum, monthly hours limit irukku. Faster ku kaasu." |
| Hugging Face la yen pannala? | "Hugging Face ippo Docker Spaces ku PRO kaasu kekkudhu. Concept same dhaan, server mattum vera." |
| Indha URL ah yaar venumnaalum call pannalaama? | "Aamaa, public. Demo ku OK. Real company la login illa API key vekkanum." |
| Image ah yen public pannrom? | "Render password illaama pull panna. Image la code um model um dhaan, rahasiyam illa. Private venum na Render la registry login kudukkalaam." |
| Indha model MLflow champion ah? | "Illa. CI train panna, check pass aana model. Real company la registry la irundhu champion ah eduthu deploy pannuvaanga. Adhu next step." |
| AWS, Azure la deploy panna mudiyumaa? | "Mudiyum. Image ah ghcr.io la vechirukkom, endha cloud um adha pull pannalam. Concept same: check pass aana dhaan ship." |

## Homework

See README Part 11: a Postman collection, a new `/version` endpoint, sending sample trips to the live API, and reading Render's free-plan limits.

**🗣 Sollunga:** "Homework la oru pudhu endpoint add panni push pannunga. Sila nimishathula unga change ulagam muzhukka live aagum. Adhu dhaan CD oda power."
