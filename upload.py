import os
import sys
import posixpath
import argparse
from subprocess import STDOUT, check_call, check_output, CalledProcessError

DEST = "s3://dvc-public/dvc-pkgs/osxpkg/"

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the osxpkg to upload")
args = parser.parse_args()

dest = posixpath.join(DEST, os.path.basename(args.path))

try:
    out = check_output(
        f"aws s3 cp {args.path} {dest} --acl public-read",
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to upload:\n{exc.output.decode()}", file=sys.stderr)
    raise
