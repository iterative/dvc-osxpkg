import os
import pathlib
import shutil
from subprocess import STDOUT, check_call, check_output

path = pathlib.Path(__file__).parent.absolute()
build = path / "build"
install = build / "usr"

flags = [
    "--description",
    '"Data Version Control | Git for Data & Models"',
    "-n",
    "dvc",
    "-s",
    "dir",
    "-f",
    "--license",
    '"Apache License 2.0"',
]

install /= "local"
bash_dir = install / "etc" / "bash_completion.d"
dirs = ["usr"]
flags.extend(
    [
        "--osxpkg-identifier-prefix",
        "com.iterative",
        "--after-install",
        path / "after-install.sh",
        "--after-remove",
        path / "after-remove.sh",
    ]
)

try:
    shutil.rmtree(build)
except FileNotFoundError:
    pass

lib = install / "lib"
lib.mkdir(parents=True)

try:
    os.rename(path / "dist" / "dvc", lib / "dvc")

    bash_dir.mkdir(parents=True)
    bash_completion = check_output(
        [lib / "dvc" / "dvc", "completion", "-s", "bash"], text=True
    )
    (bash_dir / "dvc").write_text(bash_completion)

    zsh_dir = install / "share" / "zsh" / "site-functions"
    zsh_dir.mkdir(parents=True)
    zsh_completion = check_output(
        [lib / "dvc" / "dvc", "completion", "-s", "zsh"], text=True
    )
    (zsh_dir / "_dvc").write_text(zsh_completion)

    version = check_output([lib / "dvc" / "dvc", "--version"], text=True).strip()

    check_call(
        [
            "fpm",
            "--verbose",
            "-t",
            "osxpkg",
            *flags,
            "-v",
            version,
            "-C",
            build,
            *dirs,
        ],
        cwd=path,
        stderr=STDOUT,
    )
finally:
    os.rename(lib / "dvc", path / "dist" / "dvc")
