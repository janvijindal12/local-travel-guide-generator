# Local Travel Guide Generator

A small Streamlit app for turning a destination and a traveler's interests into a short local guide. It comes with a fictional-project-sized set of Porto examples, an optional GPT-2 LoRA training path, and a lightweight relevance check.

## Run the app

You need Python 3.12 and Git. From this folder, create an environment and install the app:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/main.py
```

The default `sample` mode works without an API key. Enter Porto and interests such as `food, architecture` to see a matching example. The app stores generated guides in `artifacts/guide_history.jsonl` on your machine; that folder is excluded from Git.

## Choose a generation mode

Set `TRAVEL_GUIDE_MODE` in `.env`:

- `sample` uses the included examples and is the default.
- `groq` calls Groq. Set `GROQ_API_KEY` and optionally `GROQ_MODEL`. Install the optional client with `pip install groq`.
- `merged` loads the locally merged Hugging Face model from `MERGED_MODEL_DIR`.

Never commit `.env`. The checked-in `.env.example` contains setting names and safe defaults only.

## Train and merge a LoRA adapter

The data in `data/guides.jsonl` is intentionally small, so this is a learning path rather than a production-quality model. For a real fine-tune, add more varied, reviewed examples and verify that you have permission to use the selected model and data.

Install the optional training packages:

```bash
pip install torch transformers datasets peft accelerate
```

Then run:

```bash
python -m app.train
python -m app.merge_adapter
```

Training uses `BASE_MODEL_ID` (GPT-2 by default) and writes the adapter and merged model beneath `artifacts/`. Generated weights are ignored by Git. GPT-2 is a small base model and may produce weak or repetitive recommendations; the included sample mode is more dependable for the starter demonstration. The merge script uses PEFT's supported `merge_and_unload()` method. This starter does not include `lfllm-lflora`: that technique is not a published dependency or API in the project requirements, so the implementation uses standard PEFT LoRA injection and merging instead.

## Check quality

The app displays a simple overlap score based on destination and interest words. It helps catch obvious mismatches but is not a measure of factual accuracy, appeal, or local expertise. Review generated claims, especially current opening times, access details, and prices, before sharing a guide with a traveler.

Run the checks with:

```bash
pytest
```

## Docker

Build and start the sample app with:

```bash
docker build -t local-travel-guide-generator .
docker run --rm -p 8501:8501 local-travel-guide-generator
```

## Project layout

```text
app/                 Streamlit interface, generation, training, and merging
data/guides.jsonl      Small set of structured sample recommendations
tests/               Core and UI generation smoke checks
```

## Publish your copy

Create an empty public GitHub repository named `local-travel-guide-generator`, without adding a README or `.gitignore`. In this project folder:

```bash
git init -b main
git add .
git commit -m "Start local-travel-guide-generator from the askThili starter"
git remote add origin https://github.com/YOUR-USERNAME/local-travel-guide-generator.git
git push -u origin main
```

After each milestone, commit your work and push. Check `git status` before sharing the repository, and confirm `.env` is not tracked.
