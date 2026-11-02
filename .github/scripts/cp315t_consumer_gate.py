"""Verify ordinary VCS provenance and real installed native APIs in CI."""

from __future__ import annotations

import base64
import csv
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import av

root = Path(__file__).resolve().parents[2]
out = root / "pyav-cp315t-evidence"
out.mkdir(exist_ok=False)
assert "PYTHON_GIL" not in os.environ
assert sys.flags.gil is None and not sys._is_gil_enabled()
assert av.__version__ == "19.0.2+stablekite.1"
assert not Path(av.__file__).resolve().is_relative_to(root)
dist = importlib.metadata.distribution("av")
direct = json.loads(dist.read_text("direct_url.json") or "null")
assert direct["url"] == "https://github.com/StableKite/PyAV.git"
assert not direct["vcs_info"].get("requested_revision")
assert direct["vcs_info"]["commit_id"] == os.environ["GITHUB_SHA"]
record = dist.read_text("RECORD")
assert record
verified = 0
for relative, checksum, size in csv.reader(record.splitlines()):
    if checksum:
        path = Path(dist.locate_file(relative))
        method, expected = checksum.split("=", 1)
        digest = hashlib.file_digest(path.open("rb"), method).digest()
        assert base64.urlsafe_b64encode(digest).rstrip(b"=").decode() == expected
        assert path.stat().st_size == int(size)
        verified += 1
result = {
    "python": sys.version,
    "GIL": sys._is_gil_enabled(),
    "gil_flag": sys.flags.gil,
    "direct_url": direct,
    "RECORD_verified": verified,
    "stages": [],
}


def run(name: str, arguments: list[str], cwd: Path) -> None:
    completed = subprocess.run(
        arguments, cwd=cwd, capture_output=True, timeout=600, check=False
    )
    (out / f"{name}.stdout.log").write_bytes(completed.stdout)
    (out / f"{name}.stderr.log").write_bytes(completed.stderr)
    result["stages"].append({"name": name, "exit_code": completed.returncode})
    (out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(completed.stdout.decode(errors="replace"), flush=True)
    if completed.returncode:
        print(completed.stderr.decode(errors="replace"), file=sys.stderr, flush=True)
    assert completed.returncode == 0, name


with tempfile.TemporaryDirectory(prefix="pyav-installed-qa-") as temporary:
    qa = Path(temporary)
    shutil.copytree(root / "tests", qa / "tests")
    scripts = root / ".github/scripts"
    run(
        "real_AAC_failed_open_recovery",
        [
            sys.executable,
            "-I",
            "-B",
            str(qa / "tests/codec_context_retry.py"),
            str(Path(av.__file__).resolve().parent.parent),
        ],
        qa,
    )
    for name, script in (
        ("real_libopus_failed_open_recovery", "cp315t_libopus_retry.py"),
        ("all_native_imports_lossless_threads", "cp315t_native_contract.py"),
    ):
        run(name, [sys.executable, "-I", "-B", str(scripts / script)], qa)
    code = (
        "import sys,av,pytest; "
        "assert sys.flags.gil is None and not sys._is_gil_enabled(); "
        "result=pytest.main(sys.argv[1:]); "
        "assert not sys._is_gil_enabled(); sys.exit(result)"
    )
    run(
        "all_canonical_pytest",
        [
            sys.executable,
            "-I",
            "-B",
            "-c",
            code,
            "--import-mode=importlib",
            str(qa / "tests"),
            "--junitxml=" + str(out / "all-canonical.xml"),
        ],
        qa,
    )
    suites = ET.parse(out / "all-canonical.xml").getroot().findall("testsuite")
    assert sum(int(suite.attrib["tests"]) for suite in suites) >= 574
    assert all(
        int(suite.attrib["failures"]) == int(suite.attrib["errors"]) == 0
        for suite in suites
    )
assert sys.flags.gil is None and not sys._is_gil_enabled()
result["status"] = "PASS"
(out / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result), flush=True)
