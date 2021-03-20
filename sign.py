import argparse
import base64
import os
import sys
import tempfile
from subprocess import STDOUT, check_call, check_output, CalledProcessError

CERT_ENV = "OSXPKG_ITERATIVE_CERTIFICATE"
CERT_PASS_ENV = "OSXPKG_ITERATIVE_CERTIFICATE_PASS"

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to the osxpkg to sign")
args = parser.parse_args()

cert = os.getenv(CERT_ENV)
if not cert:
    print(f"'{CERT_ENV}' env var is required", file=sys.stderr)
    exit(1)

cert_path = "cert.pfx"
with open(cert_path, "wb") as fobj:
    fobj.write(base64.b64decode(cert))
    
cert_pass = os.getenv(CERT_PASS_ENV)
if not cert_pass:
    print(f"'{CERT_PASS_ENV}' env var is required", file=sys.stderr)
    exit(1)

if not os.path.exists(args.path):
    print(f"'{args.path}' doesn't exist", file=sys.stderr)
    exit(1)

print("=== checking for existing signature")

try:
    out = check_output(
        f"codesign --verify -d --verbose=2 {args.path}",
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output.decode()}", file=sys.stderr)
    raise

# TODO: check that it is not signed yet
print(out.decode())

# NOTE: from https://localazy.com/blog/how-to-automatically-sign-macos-apps-using-github-actions
print("=== preparing keychain")

tmp_pass = "123456"

try:
    check_call(
        f"security create-keychain -p {tmp_pass} build.keychain",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

try:
    check_call(
        f"security default-keychain -s build.keychain",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

try:
    check_call(
        f"security unlock-keychain -p {tmp_pass} build.keychain",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

try:
    check_call(
        f"security import {cert_path} -k build.keychain -P {cert_pass} -T /usr/bin/codesign",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

try:
    check_call(
        f"security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k {tmp_pass} build.keychain",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

print(f"=== looking up identity-id")

try:
    check_call(
        f"security find-identity -v",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

print(out.decode())

print(f"=== signing {args.path}")

try:
    check_call(
        f"codesign --force -s {identity_id} {args.path} -v",
        stderr=STDOUT, shell=True,
    )
except CalledProcessError as exc:
    print(f"failed to sign:\n{exc.output.decode()}", file=sys.stderr)
    raise

print("=== verifying signed executable")

try:
    out = check_output(
        f"codesign --verify -d --verbose=2 {args.path}",
        stderr=STDOUT, shell=True
    )
except CalledProcessError as exc:
    print(f"failed to check signature:\n{exc.output.decode()}", file=sys.stderr)
    raise

# TODO: check that it is properly signed
print(out.decode())

print(f"=== successfully signed '{args.path}'")
