import json
from pathlib import Path
import ee
from typing import Final

PRIVATE_KEY_PATH: Final[str] = str(Path(__file__).parent.parent / ".private_key.json")
def _get_credential_email() -> str:
    with open(PRIVATE_KEY_PATH, "r") as f:
        return json.load(f)["client_email"]

def _authenticate() -> None:
    credentials = ee.ServiceAccountCredentials(_get_credential_email(), PRIVATE_KEY_PATH)
    ee.Initialize(credentials=credentials)


if __name__ == "__main__":
    _authenticate()