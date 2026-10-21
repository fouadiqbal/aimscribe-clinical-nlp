"""Download a pinned MiniLM snapshot without optional HF transfer backends."""
import concurrent.futures
import hashlib
import urllib.request
from src.common import ROOT, write_json

REVISION="1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
FILES=["config.json","config_sentence_transformers.json","model.safetensors","modules.json",
       "sentence_bert_config.json","special_tokens_map.json","tokenizer.json","tokenizer_config.json",
       "vocab.txt","1_Pooling/config.json","README.md"]


def main():
    target=ROOT / "models/embeddings"
    if target.exists():
        print("Local embedding model already present.")
        return
    temporary=ROOT / "models/embeddings_download"
    def download(name):
        path=temporary / name
        path.parent.mkdir(parents=True,exist_ok=True)
        url=f"https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/{REVISION}/{name}?download=true"
        if not path.exists():
            with urllib.request.urlopen(url,timeout=180) as response, path.with_suffix(path.suffix+".part").open("wb") as out:
                while chunk:=response.read(1024*1024):
                    out.write(chunk)
            path.with_suffix(path.suffix+".part").replace(path)
        print(f"Ready embedding file {name}",flush=True)
        with path.open("rb") as f:
            digest=hashlib.file_digest(f,"sha256").hexdigest()
        return {"file":name,"sha256":digest,"url":url}
    with concurrent.futures.ThreadPoolExecutor(3) as pool:
        records=list(pool.map(download,FILES))
    temporary.replace(target)
    write_json(ROOT / "results/embedding_downloads.json",{"revision":REVISION,"files":records})


if __name__=="__main__":
    main()
