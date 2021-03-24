import argparse
import json
import pathlib
from subprocess import STDOUT, check_call

path = pathlib.Path(__file__).parent.absolute()

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the osxpkg to notarize")
args = parser.parse_args()

config = {
    "notarize": {
        "path": args.path,
        "bundle_id": "com.iterative.dvc",
        "staple": True,
    },
    "apple_id": {
        "username": "kupruser@gmail.com",
        "password": "@env:APPLE_ID_PASSWORD",
    },
}

(path / "config.json").write_text(json.dumps(config))

check_call(
    ["gon", "config.json"], cwd=path, stderr=STDOUT,
)
