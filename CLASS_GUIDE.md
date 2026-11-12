# Class 5 Teaching Guide: Continuous Deployment to a Live API

**Time:** about 2 hours
**Project:** the Class 4 taxi project, plus an automatic deploy to a Hugging Face Space

How to use this guide: **instructions for you are in English**. Lines marked **🗣 Sollunga** are what to say to students, in Thanglish. Commands and expected output are in `README.md`, and the Part letters match.

## By the end of class, students can

1. Explain the difference between CI and CD
2. Store a token safely as a GitHub secret
3. Say when the deploy job runs and when it doesn't
4. Call the live API from Postman and the browser
5. Ship a new version with a push, and confirm it's live

**🗣 Sollunga:** "Class 4 la GitHub check pannudhu, aana Postman la call panna mudiyala. Indha class mudiyumbodhu, unga model oru real public URL la odum. Push pannina pudhu version automatic ah live aagum."

## Before class

**You**
- [ ] Do the full flow once on your own repo: token, secret, variable, push, 4 green jobs
- [ ] Note how long the `deploy` job takes (the Hugging Face build). **It has not run on Hugging Face yet**
- [ ] Open the Space's `/health` 10 minutes before class, so it isn't asleep
- [ ] Set up a Postman request for `/predict`
- [ ] Optional: try the rollback (Part F) once

**Students**
- [ ] A Hugging Face account (free)
- [ ] Postman installed, or use the browser `/docs` page
- [ ] Their Class 4 repo, with CI green

**Decision for you:** one Space per student (each needs a token), or one shared Space that only you deploy? For a first class, one shared Space is simpler: you deploy, everyone calls your URL.

## Class plan

| Time | Part (README) | Outcome |
|---|---|---|
| 10 min | 0–1. CI vs CD | Students know what's new |
| 15 min | A. Token, secret, variable | Secrets understood and set |
| 15 min | B. Laptop check and dry run | Students see what gets shipped |
| 20 min | C. Read the `deploy` job | `needs`, `if`, `concurrency`, secrets |
| 15 min | D. Push and watch the deploy | 4 green jobs, Space running |
| 25 min | E. Live inference | Postman and `/docs` calls, `422` errors |
| 15 min | F. Ship a new version | New `model_version` appears live |
| 5 min | Wrap-up | Check understanding |

---

## Part 0–1: CI vs CD (10 min)

Draw the diagram from README Part 0.

**🗣 Sollunga:** "CI na check pannradhu. CD na, check pass aana, automatic ah ship pannradhu. GitHub Actions gatekeeper maari, nalla model ah mattum ulla vidum. Hugging Face server maari, eppovum odum, users ku answer pannum."

**Ask:** "Class 4 la Postman la yen call panna mudiyala?"
**🗣 Answer:** "GitHub Actions machine job mudinjadhum azhinjidum. Server illa. Adhunaala dhaan deploy venum."

## Part A: Token, secret, variable (15 min)

Walk through README Part A. Spend time on **why** secrets matter.

**🗣 Sollunga:** "Token na unga account oda password maari. Code la pottaa, GitHub la yaar paathaalum unga account la upload pannalam. Adhunaala GitHub **secret** la vekkanum. Save pannina apram GitHub kooda thirumba kaattaadhu. Logs la `***` nu dhaan varum."

**Ask:** "Space name ah yen secret la vekkala, variable la vechom?"
**🗣 Answer:** "Space name rahasiyam illa. Ellarum URL la paakkalaam. Token mattum dhaan rahasiyam."

⚠️ Tell students never to paste their token in chat or screenshots, including yours.

## Part B: Laptop check and dry run (15 min)

Run `pytest -v`, `check_model.py`, then `deploy_space.py --dry-run`.

**🗣 Sollunga:** "`--dry-run` upload pannaadhu. Hugging Face ku enna files pogum nu mattum kaattum. Dockerfile, code, model, matrum oru README. Andha README top la `sdk: docker`, `app_port: 8000` irukku. Adhu Hugging Face ku 'Docker vechu build pannu, port 8000 la API odum' nu sollum."

**Point out the Dockerfile change:** the app now runs as user 1000, not root.

**🗣 Sollunga:** "Hugging Face app ah user 1000 ah dhaan run pannum. Naama CI la um adhe maari run pannrom. Apo CI la pass aana, Hugging Face la um work aagum nu nambikkai."

## Part C: Read the `deploy` job (20 min)

Use the table in README Part C.

| Line | 🗣 Sollunga |
|---|---|
| `needs: docker` | "Moonu checks um pass aana dhaan deploy." |
| `if: ... refs/heads/main` | "`main` ku push panna mattum. Pull request la deploy aagaadhu. Review aagaadha code live ku pogakoodadhu." |
| `concurrency: deploy` | "Rendu push vegama vandhaalum, orey time la oru deploy dhaan. Illana rendu um mothikkum." |
| `download-artifact` | "Check pass aana adhe model dhaan live ku pogum. Pudhusa train pannala." |
| `secrets.HF_TOKEN` | "Token secret la irundhu varudhu, code la illa." |

Then walk through the 8 steps of `deploy_space.py`.

**Ask:** "Upload aana odane 'deployed' nu sollalaama?"
**🗣 Answer:** "Illa. Upload aanaalum Hugging Face la build fail aagalaam. Live URL pudhu version sollura varaikkum wait panni, oru prediction test pannina apram dhaan 'live' nu sollanum. Adhaan script pannudhu."

## Part D: Push and watch the deploy (15 min)

Push, then open the **Actions** tab. Show the 4 jobs, then expand the deploy step.

**🗣 Sollunga:** "Paarunga, `Space: BUILDING` nu varudhu. Hugging Face namma Docker image ah build pannudhu. Mudinjadhum `RUNNING` aagi, pudhu version sollum. Apram script ae oru prediction test pannum."

While it builds, open the Space page on Hugging Face and show the **Logs** tab.

## Part E: Live inference (25 min)

Open `/docs` in the browser first, then Postman. Use the tries table in README Part E. Ask before each **Send**.

**🗣 Sollunga:** "Ippo idhu real API. Unga phone la irundhu kooda call pannalam. Oru mobile app, website, yaar venumnaalum indha URL ah use pannalam."

Show the `422` errors.

**🗣 Sollunga:** "Thappana input ku model kitta poga koodaadhu. API ae reject pannum. Endha field thappu nu kooda sollum."

If the first call is slow:

**🗣 Sollunga:** "Free Space konja neram use aagala na thoongidum. Idhu cold start. Paid hardware la idhu varaadhu."

## Part F: Ship a new version (15 min)

Change the API title to "v2", push, wait for green, then press **Send** in Postman again.

**🗣 Sollunga:** "Naama Hugging Face website ah touch kooda pannala. Push mattum dhaan. Check pass aachu, adhuve ship aachu. Idhu dhaan CD."

Then explain why a bad change can't go live, using the table in README Part F.

**🗣 Sollunga:** "Weak model push pannaalum, `model-check` fail aagum, `deploy` skip aagum. Live API pazhaya nalla version laye irukkum. Users ku mosamaana model pogave pogaadhu."

---

## Check understanding

| Question | 🗣 Answer |
|---|---|
| CI um CD um enna difference? | CI check pannum. CD, pass aana, automatic ah ship pannum |
| Token ah yen code la podakoodadhu? | Yaar paathaalum unga account la upload pannalam. Secret la vechaa logs la kooda theriyaadhu |
| Pull request la deploy aagumaa? | Illa. `main` ku push panna mattum |
| Weak model push panna live API ku enna aagum? | Onnum aagaadhu. `deploy` skip, pazhaya version laye irukkum |
| Upload aana odane "deployed" nu sollalaama? | Illa. Live URL pudhu version sollura varaikkum wait panni test pannanum |
| Live la endha version odudhu nu eppadi theriyum? | `/health` illa `/predict` la `model_version` |
| First request yen slow? | Free Space thoongidum, cold start |

## Likely student questions

| Question | 🗣 Answer |
|---|---|
| Hugging Face free ah? | "Basic CPU Space free. Aana use aagala na thoongidum. Faster hardware ku kaasu." |
| Indha URL ah yaar venumnaalum call pannalaama? | "Aamaa, public Space. Demo ku OK. Real company la login illa API key vekkanum." |
| Indha model MLflow champion ah? | "Illa. CI train panna, check pass aana model. Real company la registry la irundhu champion ah eduthu deploy pannuvaanga. Adhu next step." |
| AWS, Azure la deploy panna mudiyumaa? | "Mudiyum. Deploy job la Hugging Face ku badhila andha cloud ku upload pannanum. Concept same: check pass aana dhaan ship." |

## Homework

See README Part 11: a Postman collection, a new `/version` endpoint, sending sample trips to the live API, and reading the Space's free-tier limits.

**🗣 Sollunga:** "Homework la oru pudhu endpoint add panni push pannunga. Sila nimishathula unga change ulagam muzhukka live aagum. Adhu dhaan CD oda power."
