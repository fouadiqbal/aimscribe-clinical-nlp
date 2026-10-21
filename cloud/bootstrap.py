"""Start the same pinned, free Qwen/llama.cpp CPU stack on Community Cloud."""
from functools import lru_cache
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time
import urllib.request

import streamlit as st

RUNTIME_URL = "https://github.com/ggml-org/llama.cpp/releases/download/b11786/llama-b11786-bin-ubuntu-x64.tar.gz"
RUNTIME_SHA256 = "e5ae13aa4d614cc4e4165a74ae2781e592b54153017a0af922ce3b4cab67b18c"
MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_SHA256 = "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e"
CACHE = Path.home() / ".cache" / "aimscribe"


def _download(url, destination, expected_sha256):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        digest = hashlib.file_digest(destination.open("rb"), "sha256").hexdigest()
        if digest == expected_sha256:
            return
        destination.unlink()
    partial = destination.with_suffix(destination.suffix + ".part")
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "AIMScribe-Assessment"})
        with urllib.request.urlopen(request, timeout=300) as response, partial.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
        digest = hashlib.file_digest(partial.open("rb"), "sha256").hexdigest()
        if digest != expected_sha256:
            raise RuntimeError(f"Downloaded file failed its SHA256 check: {destination.name}")
        partial.replace(destination)
    finally:
        if partial.exists():
            partial.unlink()


@lru_cache(maxsize=1)
def ensure_model_server():
    """Download on first patient case, reuse process for later interactions."""
    import urllib.error
    import urllib.request

    health = "http://127.0.0.1:8080/health"
    try:
        with urllib.request.urlopen(health, timeout=2):
            return
    except (urllib.error.URLError, TimeoutError):
        pass

    with st.status("Preparing the free local model in the cloud…", expanded=True) as status:
        model = CACHE / "qwen2.5-1.5b-instruct-q4_k_m.gguf"
        runtime_archive = CACHE / "llama-b11786-ubuntu-x64.tar.gz"
        runtime_dir = CACHE / "llama-b11786"
        binary = runtime_dir / "llama-server"
        _download(RUNTIME_URL, runtime_archive, RUNTIME_SHA256)
        runtime_dir.mkdir(parents=True, exist_ok=True)
        if not binary.exists():
            with tarfile.open(runtime_archive, "r:gz") as archive:
                root = runtime_dir.resolve()
                for member in archive.getmembers():
                    target = (runtime_dir / member.name).resolve()
                    if root not in target.parents and target != root:
                        raise RuntimeError("Unsafe path in llama.cpp release archive")
                archive.extractall(runtime_dir)
            candidates = list(runtime_dir.rglob("llama-server"))
            if not candidates:
                raise RuntimeError("The pinned llama.cpp archive has no llama-server binary")
            binary = candidates[0]
            binary.chmod(binary.stat().st_mode | 0o111)
        _download(MODEL_URL, model, MODEL_SHA256)

        environment = os.environ.copy()
        environment["LD_LIBRARY_PATH"] = str(binary.parent) + os.pathsep + environment.get("LD_LIBRARY_PATH", "")
        subprocess.Popen([str(binary), "-m", str(model), "--host", "127.0.0.1", "--port", "8080",
                          "-c", "4096", "-t", "2", "-ngl", "0", "--parallel", "1"],
                         cwd=binary.parent, env=environment, stdout=subprocess.DEVNULL,
                         stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(240):
            try:
                with urllib.request.urlopen(health, timeout=2) as response:
                    if response.status == 200:
                        status.update(label="Local model ready", state="complete", expanded=False)
                        return
            except (urllib.error.URLError, TimeoutError):
                time.sleep(1)
        raise RuntimeError("The cloud model did not start within four minutes. Check Streamlit app logs and memory limits.")
