"""Fault injection: never edit the production RTL; reject infrastructure failures."""
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "rtl/sync_fifo.sv").read_text()
mutations = {
    "early_full": ("count == DEPTH", "count == DEPTH-1"),
    "overflow_write": ("wr_en && !full", "wr_en"),
    "stuck_read_pointer": ("rd_ptr + 1'b1", "rd_ptr"),
}
summary = []
for name, (old, new) in mutations.items():
    assert source.count(old) == 1, f"Mutation anchor is ambiguous: {name}"
    target = ROOT / "build/mutations" / f"{name}.sv"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.replace(old, new))
    phase = f"phase5/{name}"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/run.py"), "--phase", phase,
                           "--suite", "directed", "--rtl", str(target)], capture_output=True, text=True)
    xml = ROOT / "results" / phase / "junit.xml"
    if not xml.exists():
        raise RuntimeError(f"{name}: no test report; infrastructure failure")
    failures = [case for case in ET.parse(xml).iter("testcase") if case.find("failure") is not None]
    log = (ROOT / "results" / phase / "simulation.log").read_text()
    assertions = [line.strip() for line in log.splitlines() if "AssertionError:" in line and "actual=" in line]
    detected = proc.returncode != 0 and bool(failures) and bool(assertions)
    summary.append({"mutation": name, "detected": detected, "failed_tests": [case.attrib["name"] for case in failures],
                    "first_assertion": assertions[0] if assertions else ""})
    if not detected:
        raise RuntimeError(f"{name}: no behavioral assertion detected the mutation")
    print(f"DETECTED {name}: {assertions[0]}")
result = ROOT / "results/phase5"
result.mkdir(parents=True, exist_ok=True)
(result / "mutation_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("PASS: all 3 deliberate faults detected; production RTL unchanged")
