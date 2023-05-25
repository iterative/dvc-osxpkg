import argparse
import os
import pathlib
import sys
from subprocess import STDOUT, check_call, CalledProcessError

if sys.platform != "darwin":
    raise NotImplementedError

parser = argparse.ArgumentParser()
parser.add_argument(
    "--application-id",
    required=True,
    help="Certificate ID (should be added to the keychain).",
)
args = parser.parse_args()

path = pathlib.Path(__file__).parent.absolute()
dvc = path / "dist" / "dvc"


for root, _, fnames in os.walk(dvc):
    for fname in fnames:
        _, ext = os.path.splitext(fname)

        if ext not in [".so", ".dylib"]:
            continue

        fpath = os.path.join(root, fname)
#        try:
#            print(f"checking signature on {fpath}")
#            check_call(
#                [
#                    "codesign",
#                    "--verify",
#                    fpath,
#                ],
#                stderr=STDOUT,
#            )
#            print(f"{fpath} is already signed, skipping...")
#            continue
#        except CalledProcessError:
#            pass
#
        print(f"signing {fpath}")
        check_call(
            [
                "codesign",
                "--force",
                "--verbose",
                "-s",
                args.application_id,
                "-o",
                "runtime",
                "--entitlements",
                "entitlements.plist",
                fpath,
            ],
            timeout=300,
            stderr=STDOUT,
        )
