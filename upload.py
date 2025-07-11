import argparse
import os
import posixpath
import sys
from subprocess import STDOUT, CalledProcessError, check_output

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the osxpkg to upload")
parser.add_argument("dest", help="destination S3 path")
args = parser.parse_args()

dest = posixpath.join(args.dest, os.path.basename(args.path))

try:
    out = check_output(
        f"aws s3 cp {args.path} {dest}",
        stderr=STDOUT,
        shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to upload:\n{exc.output.decode()}", file=sys.stderr)
    raise
