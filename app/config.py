from pathlib import Path
APP_NAME = "Demo IA Sport & Santé — LITE"
MODEL_VERSION = "v0.1.1-lite"
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
