"""Settings."""
import os
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DB = DATA / "oracle.db"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
API_KEY = os.environ.get("OPENCODE_GO_API_KEY", "")
