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

check_call(
    [
        "codesign",
        "--deep",
        "--force",
        "--verbose",
        "-s",
        args.application_id,
        "-o",
        "runtime",
        "--entitlements",
        "entitlements.plist",
        os.fspath(dvc),
    ],
    stderr=STDOUT,
)

#
#for root, _, fnames in os.walk(dvc):
#    for fname in fnames:
#        fpath = os.path.join(root, fname)
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
#        print(f"signing {fpath}")
#        check_call(
#            [
#                "codesign",
#                "--force",
#                "--verbose",
#                "-s",
#                args.application_id,
#                "-o",
#                "runtime",
#                "--entitlements",
#                "entitlements.plist",
#                fpath,
#            ],
#            stderr=STDOUT,
#        )
