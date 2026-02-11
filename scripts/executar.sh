# Executa o programa independente do terminal (nohup + disown)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
nohup env PYTHONPATH=src python3 -m src.horas_trabalhadas > /dev/null 2>&1 &
disown
exit 0

