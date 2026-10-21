# AIMScribe clinical NLP assessment

Small local RAG prototype using the four supplied protocols. A local embedding model retrieves canonical recommendation cards; a local language model selects relevant cards and explains their relevance. The interface displays curated source actions, medication fields and page references. Improved mode adds one applicability/missing-information checker.

**Current status:** implementation and 12-output experiment complete. Results are AI-assisted provisional judgments with documented failures. Candidate source verification of cards, visual transcription, checklists and grading remains pending. See results/comparison_note.md and COMPLETION_STATUS.md.

## Setup (Windows, Python 3.12)

Open PowerShell in this project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.setup_local_model
.\.venv\Scripts\python.exe -m src.setup_embeddings
.\.venv\Scripts\python.exe -m src.validate_cards
.\.venv\Scripts\python.exe -m src.index
```

Setup downloads Python packages, the approximately 1.12 GB GGUF model, the official Windows CPU llama.cpp runtime, and local MiniLM embeddings. Downloads need internet; subsequent inference is local. No API key, paid service, training or dedicated GPU is required. This version targets Windows x64; for another OS install the official llama.cpp runtime and start its server with equivalent settings.

On this prepared computer, double-click **Open_AIMScribe.cmd**. It starts persistent local services and opens http://127.0.0.1:8501/. The app needs these services running after a reboot. Logs are in results/service_logs/. Initial setup above is needed on another computer.

Alternatively, run the model in one PowerShell terminal:

```powershell
.\start_model.ps1
```

Run the interface in another:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit. Enter symptoms and available details. Leave unknown facts blank/Unknown. Expand clinical findings to provide source prerequisites. There is no disease-name input. Keep the model terminal running. The inference endpoint defaults to `http://127.0.0.1:8080/v1/chat/completions`; optional `LOCAL_MODEL_URL` can point to another compatible **local** server. No credentials are used.

If PowerShell blocks scripts, invoke llama-server.exe with the command in start_model.ps1 directly; do not change system execution policy merely for this project.

## Model and retrieval details

- Generator/selector: [Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF), Q4_K_M, Apache 2.0. Existing model; no training. It is a small general-purpose model, not a clinically validated model.
- Runtime: official [llama.cpp](https://github.com/ggml-org/llama.cpp) Windows CPU release b11786. Downloads and SHA256 are recorded in results/local_model_downloads.json.
- Settings: temperature 0, seed 42, top 8 retrieved cards, maximum 950 generated tokens, 8192-token server context, four CPU inference threads, one slot.
- Embeddings: sentence-transformers/all-MiniLM-L6-v2, on CPU, saved to models/embeddings after indexing.
- Vector storage: normalized embedding matrix in data/index/vectors.npy with stable IDs and source-card hash. Exact cosine search is appropriate for 34 cards and avoids an extra database service. Rebuild using `python -m src.index`.
- Both modes share source corpus, retrieval, settings, prompt, output schema and rendering. Only improved mode executes source rules, drops excluded cards and labels unknown prerequisites. No extra LLM call.
- Card references are checked. Source actions and medication fields are copied from cards after model selection. The model's relevance explanation still needs semantic review.

## Sources and card review

Active PDFs/editions/assigned pages are in data/protocols/manifest.json. Inventory and hashes are in results/source_inventory.json. PDF cover is page 1; printed numbering may differ. All 45 assigned positions are extracted. The 27-page chikungunya replacement is active; the earlier 24-page source is preserved but not indexed.

```powershell
.\.venv\Scripts\python.exe -m src.extract
.\.venv\Scripts\python.exe -m src.build_cards
.\.venv\Scripts\python.exe -m src.validate_cards
.\.venv\Scripts\python.exe -m src.make_review
```

`build_cards` is an explicit curated draft builder and resets review status; do not rerun it over candidate-reviewed edits without preserving them. Extraction defaults to pypdf, the backend used for evidence strings. Image-only hypertension Figure 8 has a separate AI visual transcription. It is explicitly reported as unverified by a human; automatic quote matching cannot validate it.

Open docs/card_review.html and compare each action/condition with the linked source pages. Download review decisions for corrections; the review sheet does not alter cards automatically. Field explanations, source-review notes and reasoning example are under docs/.

## Development checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests exercise unknown-versus-false handling, conclusive branches, age boundaries, severe-dehydration precedence and source-linked NSAID prerequisites. Smoke outputs use separate development cases, not the final six.

## Final comparison (after development and checklist review)

Six fictional inputs and expected checklists are under data/cases/. Case C6 changes only C4's afebrile_hours from 60 to 24. Review first; the source-supported 48-hour prerequisite should change NSAID eligibility, while relevant assessment/follow-up remains.

```powershell
.\.venv\Scripts\python.exe -m src.evaluate --freeze
.\.venv\Scripts\python.exe -m src.evaluate
```

The first command records SHA256 before final outputs. The second runs both modes on the six cases and saves 12 output attempts plus a blank grading table. Expected checklists never enter prompts or the index. Existing outputs and grades are preserved. Grade every check PASS/FAIL/NA with reasons and source pages; do not report empty checks as passes. Model/connection failures remain visible. Any rerun/change needs a separately versioned experiment; never tune frozen expectations to results.

The comparison note must report counts/denominators, times, one failure/limitation, likely and alternative explanations, and the next test. Six self-authored cases do not establish clinical accuracy. This experiment does not compare RAG against no retrieval.

## Submission checklist

- Candidate-reviewed cards and field/reasoning explanation.
- Runnable two-mode app, model setup details, requirements and index rebuild.
- Frozen six cases/checklists, 12 actual outputs, graded results table and <=1-page comparison note.
- Architecture diagram with implemented/future components, design defence and trade-off.
- 200-300-word paper summary and 5-10 slides for a roughly 10-minute talk plus live demo.
- AI_DISCLOSURE.md; candidate can explain every component and limitation.
- Final ZIP: `Md_Fouad_Iqbal_RA_Clinical_NLP.zip`. Exclude secrets, .venv, temporary files and machine-specific caches. Include model download/rebuild instructions rather than a large platform-specific runtime by default.

This is an assessment prototype for fictional examples. It has not undergone independent clinical validation.

## Optional Streamlit Community Cloud version

The deployment entry point is `cloud/app.py`. It retains the same Streamlit interface and engine, then downloads the pinned free CPU model into the cloud container on the first submitted fictional case. No API token or paid inference provider is required. The first model download is about 1.12 GB; inference may be slow or exceed Community Cloud's resource limits. Use fictional information only. Follow `cloud/README.md` for the deployment settings. The local Windows version remains available through `Open_AIMScribe.cmd`.
