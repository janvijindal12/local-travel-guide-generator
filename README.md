# Local Travel Guide Generator

This is a small guidebook for Bellwether Bay, a fictional coastal town. Pick a few interests and the app finds the hand-written example that best matches them. The sample version runs locally without an account, API key, or downloaded model.

The project also includes an optional GPT-2 LoRA training and merge path. It is here to make the fine-tuning workflow inspectable; eight short examples are far too little data to produce dependable travel advice.

## Start the app

Python 3.12 is recommended. From the project folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/main.py
```

Choose a destination and interests in the form. Try `Bellwether Bay` with `seafood` and `harbor`. The app writes guides you generate to `artifacts/guide_history.jsonl`; that local folder is ignored by Git.

## What is included

- `data/guides.jsonl` contains eight reviewed-for-consistency examples for the fictional destination. Each row has a destination, a comma-separated interest list, and a guide.
- `app/core.py` loads and validates the data, picks the example with the strongest interest match, and calculates a simple word-overlap score.
- `app/main.py` is the Streamlit interface.
- `app/train.py` trains a GPT-2 adapter with PEFT LoRA. `app/merge_adapter.py` merges the adapter into the base model for local inference.
- `app/evaluation.py` compares the hand-written guides with a generic sentence baseline and writes a JSON report.

## Run the checks and evaluation

```bash
pytest
python -m app.evaluation
```

The evaluation report is saved to `results/evaluation.json`. Its score is lexical overlap between requested destination or interest words and guide text. The current checked-in run covers all 8 examples, with a mean interest-word overlap of 0.86 for the tailored guides versus 0.03 for the generic baseline. All 8 are under the 180-word limit. The baseline is intentionally plain: “Enjoy a pleasant day exploring the area, then find a place to eat and relax.” A higher overlap score means the guide repeats more of the requested interest words. It does not prove that an idea is accurate, accessible, appealing, or currently available. Bellwether Bay is invented, so the examples are for demonstrating matching and evaluation only.

## Optional model training

The app defaults to `TRAVEL_GUIDE_MODE=sample`. To experiment with LoRA, install the additional packages:

```bash
pip install torch transformers datasets peft accelerate
```

Then train and merge:

```bash
python -m app.train
python -m app.merge_adapter
```

The default base model is GPT-2. `BASE_MODEL_ID`, `TRAINING_OUTPUT_DIR`, and `MERGED_MODEL_DIR` can be changed in `.env`. Model files are large and remain local under `artifacts/`, which Git ignores. To use the merged model in the app, set `TRAVEL_GUIDE_MODE=merged` in `.env` and restart Streamlit.

The starter brief refers to `lfllm-lflora`. The checked-in implementation uses PEFT's documented LoRA adapter injection and merge API instead. It does not claim to implement that separately named technique. The tiny dataset is also not enough to establish that fine-tuning improves guide quality; the included score only checks word overlap against a generic baseline.

For hosted generation, the optional Groq mode can be enabled with `TRAVEL_GUIDE_MODE=groq` and a `GROQ_API_KEY` in `.env`. Install its client with `pip install groq`. Do not commit `.env`; `.env.example` contains only safe defaults.

## Docker

```bash
docker build -t local-travel-guide-generator .
docker run --rm -p 8501:8501 local-travel-guide-generator
```

## GitHub

The workflow in `.github/workflows/ci.yml` installs the app requirements and runs the test suite on pushes and pull requests. To publish your own copy, create an empty public GitHub repository named `local-travel-guide-generator`, without adding a README or `.gitignore`, then run:

```bash
git init -b main
git add .
git commit -m "Start local-travel-guide-generator from the askThili starter"
git remote add origin https://github.com/YOUR-USERNAME/local-travel-guide-generator.git
git push -u origin main
```

After that, commit each finished piece of work and push it with `git push`. `git status` should be clean when your work is committed. Keep real credentials and model weights out of the repository.
