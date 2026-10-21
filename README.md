# AIMScribe

Streamlit prototype for source-linked recommendations from four clinical protocols. It supports editable patient context, exact embedding retrieval, a local language model and baseline/improved applicability-checker modes.

## Deploy on Streamlit Community Cloud

Choose this repository, branch `master`, and entry point `cloud/app.py`. The deployment uses the adjacent `cloud/requirements.txt`, the included `data/cards/` and `data/index/`, and shared modules under `src/`.

On the first submitted fictional case, the app downloads the pinned Qwen 1.5B quantized model (about 1.12 GB) and official llama.cpp Linux CPU runtime into its cloud container. SHA256 checks run before the model starts. It uses no API key. Initial setup and CPU inference can be slow; the free Community Cloud resource limit may prevent inference. The app warns viewers to use fictional information only. It is an educational prototype, not a clinical service.

See `cloud/README.md` for model details and troubleshooting. For the prepared Windows computer, use `Open_AIMScribe.cmd` and the local model.

The public Cloud deployment is [AIMScribe on Streamlit](https://aimscribe-clinical-nlp-fbfmk4svhrd9kqxfbamuow.streamlit.app/). Its container starts, but the page is currently stuck on Streamlit's loading spinner, so the hosted demo is not yet verified as usable. Use the local launcher for demonstrations until the hosted page renders and a fictional inference is checked.
