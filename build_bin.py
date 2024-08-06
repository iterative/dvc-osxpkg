import os
import pathlib
from subprocess import STDOUT, CalledProcessError, check_call, check_output

path = pathlib.Path(__file__).parent.absolute()
dvc = path / "dvc" / "dvc"
entry = dvc / "__main__.py"

check_call(
    [
        "pyinstaller",
        "--name",
        "dvc",
        "-y",
        os.fspath(entry),
    ],
    cwd=path,
    stderr=STDOUT,
)

try:
    out = check_output(
        [
            path / "dist" / "dvc" / "dvc",
            "doctor",
        ],
        stderr=STDOUT,
    ).decode()
except CalledProcessError as exc:
    out = exc.output.decode()
    print(out)
    raise

remotes = [
    "s3",
    "oss",
    "gdrive",
    "gs",
    "hdfs",
    "http",
    "webhdfs",
    "azure",
    "ssh",
    "webdav",
]

print(out)
assert "(osxpkg)" in out.splitlines()[0]
for remote in remotes:
    assert f"\t{remote}" in out, f"Missing support for {remote}"
