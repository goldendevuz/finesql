import json
import urllib.request
import re
import sys
from pathlib import Path

# =========================
# CONFIG
# =========================

MODE = "file"  # "list" or "file"
INPUT_FILE = "requirements.txt"
OUTPUT_FILE = "requirements.lock.txt"

PACKAGES_LIST = [
    "aiofiles","aiogram","aiohappyeyeballs","aiohttp","aiosignal","alembic",
    "annotated-types","anyio","async-timeout","asyncpg","attrs","Babel",
    "bcrypt","certifi","click","exceptiongroup","frozenlist","greenlet",
    "h11","idna","itsdangerous","Jinja2","magic-filter","Mako","MarkupSafe",
    "multidict","pi","propcache","psycopg2-binary","pydantic","pydantic_core",
    "python-dotenv","python-multipart","pytz","setuptools","sniffio",
    "SQLAlchemy","starlette","starlette-admin","typing_extensions","uvicorn","yarl"
]

PYPI_URL = "https://pypi.org/pypi/{}/json"

# =========================
# HELPERS
# =========================

PKG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")

def extract_name(line: str) -> str | None:
    """
    Extract package name from lines like:
      pkg
      pkg==1.2.3
      pkg>=1.0
      pkg~=2.0
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    match = PKG_RE.match(line)
    return match.group(0) if match else None


def load_packages() -> list[str]:
    if MODE == "list":
        return PACKAGES_LIST

    if MODE == "file":
        path = Path(INPUT_FILE)
        if not path.exists():
            raise FileNotFoundError(f"{INPUT_FILE} not found")

        names = []
        for line in path.read_text(encoding="utf-8").splitlines():
            name = extract_name(line)
            if name:
                names.append(name)
        return names

    raise ValueError("MODE must be 'list' or 'file'")


def latest_version(pkg: str) -> str:
    with urllib.request.urlopen(PYPI_URL.format(pkg), timeout=10) as r:
        data = json.load(r)
        return data["info"]["version"]

# =========================
# MAIN
# =========================

packages = load_packages()
seen = set()

out = open(OUTPUT_FILE, "w", encoding="utf-8")

for pkg in packages:
    pkg_l = pkg.lower()
    if pkg_l in seen:
        continue
    seen.add(pkg_l)

    try:
        version = latest_version(pkg)
        line = f"{pkg}=={version}"
    except Exception as e:
        line = f"# FAILED {pkg}: {e}"

    # console (live)
    print(line, flush=True)

    # file
    out.write(line + "\n")
    out.flush()

out.close()
