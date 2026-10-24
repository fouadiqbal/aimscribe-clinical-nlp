$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskServer = Get-ChildItem -LiteralPath 'runtime/llama' -Filter 'llama-server.exe' -Recurse | Select-Object -First 1
if (-not $taskServer) { throw 'Run python -m src.setup_local_model first.' }
& $taskServer.FullName -m 'models/qwen2.5-1.5b-instruct-q4_k_m.gguf' --host 127.0.0.1 --port 8080 -c 8192 -t 4 -ngl 0 --parallel 1
