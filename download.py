import os
import pathlib
import posixpath
import shutil
import tarfile

import wget

VERSION = "1a25ebe3bd2eda4c3612e408fb503d64490fb56c"
URL = f"https://github.com/iterative/dvc/archive/{VERSION}.tar.gz"

path = pathlib.Path(__file__).parent.absolute()
dvc = path / "dvc"

try:
    shutil.rmtree(dvc)
except FileNotFoundError:
    pass

tar = path / posixpath.basename(URL)

try:
    tar.unlink()
except FileNotFoundError:
    pass

wget.download(URL, out=os.fspath(tar))

with tarfile.open(tar) as tobj:
    tobj.extractall()

os.rename(tar.with_name(f"dvc-{VERSION}"), dvc)
