import argparse
import os
import pathlib
from subprocess import STDOUT, check_call

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the osxpkg to sign")
parser.add_argument("--application-id", required=True)
parser.add_argument("--installer-id", required=True)
args = parser.parse_args()

pkg = pathlib.Path(args.path)
unpacked = pkg.with_suffix(".unpacked")

check_call(
    ["pkgutil", "--expand-full", os.fspath(pkg), os.fspath(unpacked)],
    stderr=STDOUT,
)

payload = unpacked / "Payload"
for root, _, fnames in os.walk(payload):
    for fname in fnames:
        path = os.path.join(root, fname)
        print(f"signing {path}")
        check_call(
            ["codesign", "--force", "-s", args.application_id, path],
            stderr=STDOUT,
        )

dvc = payload / "usr" / "local" / "lib" / "dvc" / "dvc"

# https://github.com/pyinstaller/pyinstaller/issues/4629
check_call(
    [
        "codesign",
        "--force",
        "-s",
        args.application_id,
        "--entitlements",
        "entitlements.plist",
        os.fspath(dvc),
    ],
    stderr=STDOUT,
)

# make sure dvc still works
check_call([os.fspath(dvc), "doctor"], stderr=STDOUT)

check_call(
    ["pkgutil", "--flatten", os.fspath(unpacked), os.fspath(pkg)],
    stderr=STDOUT,
)

signed = pkg.with_suffix(".signed")
check_call(
    [
        "productsign",
        "--sign",
        args.installer_id,
        os.fspath(pkg),
        os.fspath(signed),
    ],
    stderr=STDOUT,
)

os.unlink(args.path)
os.rename(signed, args.path)

check_call(
    ["pkgutil", "--check-signature", os.fspath(pkg)], stderr=STDOUT,
)
