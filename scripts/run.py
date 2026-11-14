"""Portable Python runner; each invocation saves a transcript and JUnit evidence."""
import argparse
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--suite", choices=["smoke", "basic", "directed", "random"], default="directed")
    parser.add_argument("--width", type=int, default=8)
    parser.add_argument("--depth", type=int, default=16)
    parser.add_argument("--rtl", type=Path)
    parser.add_argument("--waves", action="store_true")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.width < 1 or args.depth < 2:
        parser.error("WIDTH must be >=1 and DEPTH must be >=2")
    if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", args.phase):
        parser.error("phase must be a relative label such as local or phase5/restored")
    result = ROOT / "results" / args.phase
    result.mkdir(parents=True, exist_ok=True)
    source = (args.rtl or ROOT / ("tb/smoke.sv" if args.suite == "smoke" else "rtl/sync_fifo.sv")).resolve()
    if not args.child:
        # Remove only generated evidence in this selected run directory, avoiding stale passes.
        for previous in result.iterdir():
            if previous.is_file() and previous.suffix in {".json", ".xml", ".csv", ".log", ".fst"}:
                previous.unlink()
        command = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], "--child"]
        proc = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # Keep published logs portable and avoid exposing workstation paths.
        output = proc.stdout.replace(str(ROOT.parents[1]), "<workspace>").replace(str(ROOT), "<project>")
        (result / "simulation.log").write_text(output, encoding="utf-8")
        print(output)
        xml_path = result / "junit.xml"
        if xml_path.exists():
            xml_path.write_text(xml_path.read_text().replace(str(ROOT) + os.sep, ""), encoding="utf-8")
        metadata = {"suite": args.suite, "width": args.width, "depth": args.depth,
                    "python": sys.version.split()[0], "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "exit_code": proc.returncode}
        (result / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")
        return proc.returncode

    from cocotb_tools.runner import get_runner
    import cocotb
    print(f"cocotb={cocotb.__version__}; python={sys.version.split()[0]}")
    smoke = args.suite == "smoke"
    top = "smoke" if smoke else "sync_fifo"
    build = ROOT / "build" / args.phase
    runner = get_runner("icarus")
    runner.build(sources=[source], hdl_toplevel=top, build_dir=build, always=True, waves=args.waves,
                 parameters={} if smoke else {"WIDTH": args.width, "DEPTH": args.depth},
                 build_args=["-g2012", "-Wall"], timescale=("1ns", "1ps"))
    sys.path.insert(0, str(ROOT / "tb"))
    xml = result / "junit.xml"
    if xml.exists():
        xml.unlink()
    runner.test(hdl_toplevel=top, test_module="test_smoke" if smoke else "test_fifo",
                build_dir=build, test_dir=build, results_xml=str(xml),
                seed=20261114, waves=args.waves,
                extra_env={"FIFO_SUITE": args.suite, "FIFO_WIDTH": str(args.width),
                           "FIFO_DEPTH": str(args.depth), "FIFO_RESULTS": str(result)})
    tree = ET.parse(xml)
    tests = list(tree.iter("testcase"))
    failures = list(tree.iter("failure")) + list(tree.iter("error"))
    skipped = list(tree.iter("skipped"))
    executed = len(tests) - len(skipped)
    if not executed or failures:
        print(f"FAIL: {len(tests)} tests, {len(failures)} failures/errors")
        return 1
    if args.waves:
        waveform = build / f"{top}.fst"
        assert waveform.exists() and waveform.stat().st_size > 0, "Missing waveform"
        shutil.copy2(waveform, result / waveform.name)
    print(f"PASS: {executed} tests; {len(skipped)} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
