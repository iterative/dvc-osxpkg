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
parser.add_argument(
    "--keychain",
    required=False,
    help="Specify a specific keychain to search for the signing identity.",
)
args = parser.parse_args()

path = pathlib.Path(__file__).parent.absolute()
dvc = path / "dist" / "dvc"

flags = []
if args.keychain:
    flags.extend(["--keychain", args.keychain])

check_call(
    [
        "codesign",
        "--force",
        "--verbose",
        "-s",
        args.application_id,
        *flags,
        "-o",
        "runtime",
        "--entitlements",
        "entitlements.plist",
        "--timestamp",
        "--pagesize",
        "0",
        "dist/dvc/dvc",
    ],
    timeout=300,
    stderr=STDOUT,
)

#for root, _, fnames in os.walk(dvc):
#    for fname in fnames:
#        _, ext = os.path.splitext(fname)
#
#        if ext not in [".so"]:#, ".dylib"]:
#            continue
#
#        fpath = os.path.join(root, fname)
#        print(f"signing {fpath}")
#        check_call(
#            [
#                "codesign",
#                "--force",
#                "--verbose",
#                "-s",
#                args.application_id,
#                *flags,
#                "-o",
#                "runtime",
#                "--entitlements",
#                "entitlements.plist",
#                fpath,
#            ],
#            timeout=300,
#            stderr=STDOUT,
#        )
