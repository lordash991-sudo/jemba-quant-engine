from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"
MODEL_DIR = ROOT_DIR / "models"
DATABASE_DIR = ROOT_DIR / "database"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)
