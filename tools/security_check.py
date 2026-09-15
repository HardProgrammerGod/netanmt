"""Small dependency-free repository secret scan for accidental commits."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "Telegram bot token": re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"),
    "JWT-like secret": re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
    "Supabase secret key": re.compile(r"\bsb_secret_[A-Za-z0-9_-]{20,}\b"),
}

hits = []
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.name == ".env" or path.suffix in {".zip", ".jpg", ".jpeg", ".png", ".pyc"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for label, pattern in PATTERNS.items():
        if pattern.search(text):
            hits.append(f"{label}: {path.relative_to(ROOT)}")

if hits:
    raise SystemExit("Potential committed secrets:\n" + "\n".join(hits))
print("SECURITY_CHECK_OK: no obvious committed tokens/keys found")
