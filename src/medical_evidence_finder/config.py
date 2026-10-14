"""Project paths and settings that work both locally and on Google Colab.

Path resolution order (for both DATA_DIR and RESULTS_DIR):
- Environment variable override (MEF_DATA_DIR / MEF_RESULTS_DIR)
- On Colab with Google Drive mounted: /content/drive/MyDrive/medical-evidence-finder/
- On Colab without Drive: /content/medical-evidence-finder/ (lost when the runtime resets)
- Locally: data/ and results/ at the project root
"""

import os
import sys
import warnings
from pathlib import Path

PROJECT_NAME = "medical-evidence-finder"

IN_COLAB = "google.colab" in sys.modules or "COLAB_RELEASE_TAG" in os.environ

DRIVE_ROOT = Path("/content/drive/MyDrive")


def _project_root() -> Path:
    # config.py lives at <root>/src/medical_evidence_finder/config.py
    root = Path(__file__).resolve().parents[2]
    if (root / "pyproject.toml").exists():
        return root
    # Package was installed non-editable (e.g. into site-packages); fall back to cwd.
    return Path.cwd()


def _base_dir() -> Path:
    if not IN_COLAB:
        return _project_root()
    if DRIVE_ROOT.exists():
        return DRIVE_ROOT / PROJECT_NAME
    warnings.warn(
        "Running on Colab without Google Drive mounted; data and results will be "
        "lost when the runtime resets. Run `from google.colab import drive; "
        "drive.mount('/content/drive')` before importing this module to persist them.",
        stacklevel=2,
    )
    return Path("/content") / PROJECT_NAME


_BASE_DIR = _base_dir()

DATA_DIR = Path(os.environ.get("MEF_DATA_DIR", _BASE_DIR / "data"))
RESULTS_DIR = Path(os.environ.get("MEF_RESULTS_DIR", _BASE_DIR / "results"))

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_colab_secrets(
    names: tuple[str, ...] = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION"),
) -> None:
    """Copy Colab Secrets into environment variables so boto3 can find them.

    No-op outside Colab (locally, boto3 reads ~/.aws/credentials or env vars)
    """
    if not IN_COLAB:
        return
    from google.colab import userdata

    for name in names:
        try:
            os.environ[name] = userdata.get(name)
        except Exception:  # SecretNotFoundError, or notebook access not granted
            warnings.warn(f"Colab secret {name!r} not found; add it via the key icon in the sidebar")

REGION = "us-east-1"
EMBED_MODEL = "amazon.titan-embed-text-v2:0"
CHAT_MODEL = "REPLACE_WITH_YOUR_CHAT_MODEL_ID"
S3_BUCKET = "REPLACE_WITH_YOUR_BUCKET_NAME"
PROMPT_VERSION = "v1"
