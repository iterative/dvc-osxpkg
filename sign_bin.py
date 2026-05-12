import argparse
import os
import pathlib
import sys
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from subprocess import STDOUT, check_call

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


def sign(fpath):
    print(f"signing {fpath}")
    check_call(
        [
            "codesign",
            "-s",
            args.application_id,
            *flags,
            "-f",
            "-v",
            "--timestamp",
            "-o",
            "runtime",
            "--entitlements",
            "entitlements.plist",
            fpath,
        ],
        timeout=60,
        stderr=STDOUT,
    )


# Symlinks resolve to the same bytes as their target, so signing both paths
# races on the same file. Skip them; the canonical entry still gets signed.
targets = (
    os.path.join(root, fname)
    for root, _, fnames in os.walk(dvc)
    for fname in fnames
    if not os.path.islink(os.path.join(root, fname))
)

max_workers = min(32, (os.cpu_count() or 1) + 4)
executor = ThreadPoolExecutor(max_workers=max_workers)
try:
    pending = set()
    for fpath in targets:
        if len(pending) >= max_workers:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            for f in done:
                f.result()
        pending.add(executor.submit(sign, fpath))
    for f in pending:
        f.result()
finally:
    executor.shutdown(wait=True, cancel_futures=True)
