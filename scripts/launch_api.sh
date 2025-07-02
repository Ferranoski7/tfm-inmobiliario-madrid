cd "$(dirname "$0")/.."
uvicorn api.main:app --reload