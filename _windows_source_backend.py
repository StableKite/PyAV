"""Build CPython 3.15t Windows wheels using the pinned upstream FFmpeg SDK."""

import hashlib
import os
import shlex
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from urllib.request import urlopen

SDK_URL = (
    "https://github.com/PyAV-Org/pyav-ffmpeg/releases/download/9.0.2-2/"
    "ffmpeg-windows-x86_64.tar.gz"
)
SDK_SHA256 = "647a8f6d7d5f6e78ce9d33b8ea43b1f98eb1055e69ac5de26b31ecfe8b45142d"
SDK_BYTES = 32263594


def enabled(config_settings=None):
    return (
        not config_settings
        and sys.platform == "win32"
        and sys.version_info[:2] == (3, 15)
        and sysconfig.get_platform() == "win-amd64"
        and sysconfig.get_config_var("Py_GIL_DISABLED") == 1
        and not any(
            os.environ.get(name)
            for name in ("CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "CC", "CXX")
        )
    )


def build_wheel(backend, wheel_directory, metadata_directory=None):
    target = Path(wheel_directory).resolve()
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pyav-ffmpeg-") as temporary:
        work = Path(temporary).resolve()
        archive = work / "sdk.tar.gz"
        digest = hashlib.sha256()
        size = 0
        with urlopen(SDK_URL, timeout=120) as response, archive.open("xb") as output:
            while chunk := response.read(1024 * 1024):
                size += len(chunk)
                if size > SDK_BYTES:
                    raise RuntimeError("Upstream FFmpeg SDK exceeds its recorded size")
                digest.update(chunk)
                output.write(chunk)
        if size != SDK_BYTES or digest.hexdigest() != SDK_SHA256:
            raise RuntimeError("Upstream FFmpeg SDK size or SHA256 mismatch")
        sdk = work / "sdk"
        sdk.mkdir()
        with tarfile.open(archive) as packed:
            for member in packed.getmembers():
                path = PurePosixPath(member.name)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or ":" in member.name
                    or "\\" in member.name
                    or not (member.isfile() or member.isdir())
                ):
                    raise RuntimeError("Unexpected FFmpeg SDK archive member")
            packed.extractall(sdk, filter="data")
        # ZIP cannot store pre-1980 timestamps carried by some SDK members.
        for path in sdk.rglob("*"):
            if path.is_file() and path.stat().st_mtime < 315619200:
                os.utime(path, (315619200, 315619200))
        if not (sdk / "include/libavcodec/avcodec.h").is_file():
            raise RuntimeError("Upstream FFmpeg SDK header is absent")
        raw = work / "raw-wheels"
        raw.mkdir()
        settings = {"--build-option": [shlex.quote("--ffmpeg-dir=" + sdk.as_posix())]}
        name = backend.build_wheel(str(raw), settings, metadata_directory)
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "delvewheel",
                "repair",
                "--add-path",
                str(sdk / "bin"),
                "-w",
                str(target),
                str(raw / name),
            ]
        )
        if not (target / name).is_file():
            raise RuntimeError("DLL repair did not produce the requested wheel")
        return name
