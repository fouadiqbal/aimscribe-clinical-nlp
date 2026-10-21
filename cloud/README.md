# Streamlit Community Cloud deployment

This entry point uses the same 34 cards, embeddings, applicability checker, Qwen model and llama.cpp version as the local prototype. It downloads the pinned CPU runtime and model from official release/model pages on the first submitted fictional case and checks both files against recorded SHA256 values. The model stays in the Streamlit container; no model API key or paid inference service is used.

Deploy repository branch `master` with **Main file path** `cloud/app.py`. The `cloud/requirements.txt` file keeps the cloud environment dependencies beside that entry point. The data card file, exact cosine index (`data/index/`) and shared Python modules must be included in the repository. Do not commit model weights, runtime downloads, secrets, or the full assessment archive.

The first request downloads about 1.2 GB and can take several minutes. Subsequent requests are faster while the container remains awake. The free service has limited CPU and memory, so a cold start can be slow or exceed its resource limit. The app is for fictional educational cases only; it has no login or patient-data controls and must not receive real patient information.

The app may hibernate when idle; open its Streamlit URL to wake it. For a presentation, warm the app with a fictional case before the interview. If inference exceeds memory, fails to build, or remains too slow, present the verified local version from `Open_AIMScribe.cmd` and describe cloud deployment as a limitation rather than claiming the online app works.
