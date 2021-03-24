import argparse
import os
import pathlib
import shutil
from subprocess import STDOUT, check_call

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the osxpkg to sign")
parser.add_argument("--application-id", required=True)
parser.add_argument("--installer-id", required=True)
args = parser.parse_args()

pkg = pathlib.Path(args.path)
unpacked = pkg.with_suffix(".unpacked")

check_call(
    ["pkgutil", "--expand", os.fspath(pkg), os.fspath(unpacked)],
    stderr=STDOUT,
)

payload = unpacked / "Payload"
payload_unpacked = payload.with_suffix(".unpacked")
payload_unpacked.mkdir()
check_call(
    ["tar", "-xvf", os.fspath(payload), "-C", os.fspath(payload_unpacked)],
    stderr=STDOUT,
)

for root, _, fnames in os.walk(payload_unpacked):
    for fname in fnames:
        path = os.path.join(root, fname)
        check_call(
            ["codesign", "--force", "-s", args.application_id, path],
            stderr=STDOUT,
        )

check_call(
    [
        "tar",
        "-czvf",
        os.fspath(payload),
        "-C",
        os.fspath(payload_unpacked),
        ".",
    ],
    stderr=STDOUT,
)

shutil.rmtree(payload_unpacked)

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
