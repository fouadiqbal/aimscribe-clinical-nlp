"""Download official free CPU inference runtime and model; no credentials needed."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = "b11786"
MODEL = "qwen2.5-1.5b-instruct-q4_k_m.gguf"
DOWNLOADS = {
    ROOT / "runtime" / f"llama-{BUILD}-bin-win-cpu-x64.zip":
        f"https://github.com/ggml-org/llama.cpp/releases/download/{BUILD}/llama-{BUILD}-bin-win-cpu-x64.zip",
    ROOT / "models" / MODEL:
        f"https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/{MODEL}",
}


def download(item):
    path, url = item
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        temporary = path.with_suffix(path.suffix + ".part")
        print(f"Downloading {path.name}", flush=True)
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as out:
            while block := response.read(1024 * 1024):
                out.write(block)
        temporary.replace(path)
    digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
    print(f"Ready {path.name}: {path.stat().st_size} bytes", flush=True)
    return {"file": str(path.relative_to(ROOT)), "url": url, "sha256": digest}


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(download, DOWNLOADS.items()))
    archive = next(p for p in DOWNLOADS if p.suffix == ".zip")
    with zipfile.ZipFile(archive) as z:
        z.extractall(ROOT / "runtime/llama")
    (ROOT / "results/local_model_downloads.json").write_text(json.dumps(records, indent=2), "utf-8")


if __name__ == "__main__":
    main()
