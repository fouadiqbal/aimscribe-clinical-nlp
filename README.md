# AIMScribe

Streamlit prototype for source-linked recommendations from four clinical protocols. It supports editable patient context, exact embedding retrieval, a local language model and baseline/improved applicability-checker modes.

## Deploy on Streamlit Community Cloud

Choose this repository, branch `master`, and entry point `cloud/app.py`. The deployment uses the adjacent `cloud/requirements.txt`, the included `data/cards/` and `data/index/`, and shared modules under `src/`.

On the first submitted fictional case, the app downloads the pinned Qwen 1.5B quantized model (about 1.12 GB) and official llama.cpp Linux CPU runtime into its cloud container. SHA256 checks run before the model starts. It uses no API key. Initial setup and CPU inference can be slow; the free Community Cloud resource limit may prevent inference. The app warns viewers to use fictional information only. It is an educational prototype, not a clinical service.

See `cloud/README.md` for model details and troubleshooting. For the prepared Windows computer, use `Open_AIMScribe.cmd` and the local model.

## Free local setup (Windows x64, Python 3.11)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force results
.\.venv\Scripts\python.exe -m src.setup_local_model
.\.venv\Scripts\python.exe -m src.setup_embeddings
.\Open_AIMScribe.cmd
```

The repository includes cards and the frozen vector index. Initial downloads require internet and several GB of free disk space. Model inference runs on CPU without API credentials. Open `http://127.0.0.1:8501/` after the launcher starts the model and interface. Run engineering tests with `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`.

Each recommendation displays its source title, edition, PDF page and card ID. Retrieved evidence contains the supporting passage. Source references do not guarantee that model-written reasons are correct. Diagnosis cards DEN-DX-01 and CHO-DX-01 carry visible terminology-review notes; the original corpus and experiment are preserved. A cloud startup health check now runs on every case so a stopped model process can be restarted.

The public deployment is [AIMScribe on Streamlit](https://aimscribe-clinical-nlp-fbfmk4svhrd9kqxfbamuow.streamlit.app/). On 24 October 2026, an improved-mode fictional case completed in 100.6 seconds with downloadable JSON and no structural validation errors. It runs independently of the Windows laptop and uses no paid model API. Free hosting can sleep or restart; allow cold-start time. Duplicate recommendations and repetitive questions remain: execution verification is not clinical validation. Keep the local launcher as an interview backup.
