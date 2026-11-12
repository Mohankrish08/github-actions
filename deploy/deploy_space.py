"""Deploy the checked model and the API to a Hugging Face Space, then test the live URL.

Needs two environment variables:
    HF_TOKEN   a Hugging Face access token with write permission
    HF_SPACE   the Space to deploy to, for example your-name/taxi-api

Usage:
    python deploy/deploy_space.py            deploy, then wait until the new version is live
    python deploy/deploy_space.py --dry-run  only prepare the files and list them
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

FILES = ["Dockerfile", "pyproject.toml"]  # copied as they are
FOLDERS = ["src", "model"]  # the API code and the model that passed the check
WAIT_MINUTES = 20  # building the image on Hugging Face takes a few minutes
FAILED_STAGES = {"BUILD_ERROR", "RUNTIME_ERROR", "CONFIG_ERROR"}
TEST_TRIP = {"PULocationID": 74, "DOLocationID": 75, "trip_distance": 2.5, "hour": 8, "weekday": 1}

# Hugging Face reads the settings at the top of the Space's README
SPACE_README = """---
title: Taxi Trip Duration API
emoji: 🚕
colorFrom: yellow
colorTo: gray
sdk: docker
app_port: 8000
pinned: false
---

# Taxi trip duration API

Predicts how many minutes a NYC green taxi trip will take.

- Model version: `{version}`
- Try it: open `/docs`
- `POST /predict` with JSON such as:

```json
{trip}
```
"""


def prepare_files(version):
    """Copy everything the Space needs into a new folder, and add the Space README."""
    folder = Path(tempfile.mkdtemp(prefix="space-"))
    for file in FILES:
        shutil.copy(file, folder / file)
    for name in FOLDERS:
        shutil.copytree(name, folder / name, ignore=shutil.ignore_patterns("__pycache__"))
    readme = SPACE_README.format(version=version, trip=json.dumps(TEST_TRIP))
    (folder / "README.md").write_text(readme, encoding="utf-8")
    return folder


def call(url, token, body=None):
    """GET the URL, or POST the body as JSON, and return the JSON answer."""
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "taxi-class-5-deploy"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read())


def wait_until_live(api, space, host, version, token):
    """Wait until the live API reports the new model version. Stop early if the build failed."""
    deadline = time.time() + WAIT_MINUTES * 60
    while time.time() < deadline:
        stage = api.get_space_runtime(space).stage
        if stage in FAILED_STAGES:
            sys.exit(f"FAILED: the Space stopped with {stage}. Logs: https://huggingface.co/spaces/{space}?logs=build")
        try:
            live_version = call(f"{host}/health", token)["model_version"]
        except Exception:
            live_version = "not answering yet"
        print(f"Space: {stage:<16} live version: {live_version}")
        if live_version == version:
            return
        time.sleep(20)
    sys.exit(f"FAILED: version {version} was not live after {WAIT_MINUTES} minutes")


def write_summary(text):
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")  # set by GitHub Actions
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as summary:
            summary.write(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="only prepare and list the files")
    args = parser.parse_args()

    version_file = Path("model/version.txt")
    if not version_file.exists():
        sys.exit("No model/ folder. Run python src/check_model.py first")
    version = version_file.read_text().strip()

    folder = prepare_files(version)
    print(f"Prepared version {version} in {folder}:")
    for file in sorted(folder.rglob("*")):
        if file.is_file():
            print("  ", file.relative_to(folder).as_posix())
    if args.dry_run:
        return

    token = os.environ.get("HF_TOKEN")
    space = os.environ.get("HF_SPACE")
    if not token or not space:
        sys.exit("Set HF_TOKEN and HF_SPACE first. On GitHub: Settings > Secrets and variables > Actions")

    from huggingface_hub import HfApi  # only needed for a real deploy

    api = HfApi(token=token)
    api.create_repo(space, repo_type="space", space_sdk="docker", exist_ok=True)
    api.upload_folder(
        repo_id=space, repo_type="space", folder_path=folder, commit_message=f"Deploy model {version}"
    )
    host = api.space_info(space).host
    print(f"Uploaded to https://huggingface.co/spaces/{space}. Waiting for {host} ...")

    wait_until_live(api, space, host, version, token)
    answer = call(f"{host}/predict", token, TEST_TRIP)
    print(f"LIVE: {host}/predict answered {answer}")

    write_summary(
        f"""### 🚀 Deployed model `{version}`

| | |
|---|---|
| Live API | {host} |
| Try it in the browser | {host}/docs |
| Postman | `POST {host}/predict` |
| Test prediction | {answer['minutes']} minutes for `{json.dumps(TEST_TRIP)}` |
"""
    )


if __name__ == "__main__":
    main()
