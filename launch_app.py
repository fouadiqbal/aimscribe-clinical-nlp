"""Start persistent local services and open the interface. No paid API."""
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent

def healthy(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False

def start(command, name):
    logs = ROOT / 'results' / 'service_logs'
    logs.mkdir(parents=True, exist_ok=True)
    with (logs / (name + '.log')).open('ab') as out:
        subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=out,
                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

if __name__ == '__main__':
    if not healthy('http://127.0.0.1:8080/health'):
        start([str(ROOT/'runtime/llama/llama-server.exe'), '-m', str(ROOT/'models/qwen2.5-1.5b-instruct-q4_k_m.gguf'), '--host','127.0.0.1','--port','8080','-c','8192','-t','4','-ngl','0','--parallel','1'], 'model')
    if not healthy('http://127.0.0.1:8501/_stcore/health'):
        start([sys.executable,'-m','streamlit','run',str(ROOT/'app.py'),'--server.address','127.0.0.1','--server.port','8501','--server.headless','true'], 'app')
    for _ in range(60):
        if healthy('http://127.0.0.1:8501/_stcore/health'):
            webbrowser.open('http://127.0.0.1:8501/')
            print('App: http://127.0.0.1:8501/ . Model may take a minute to load.')
            break
        time.sleep(1)
    else:
        raise SystemExit('App did not start. Check results/service_logs/app.log')
