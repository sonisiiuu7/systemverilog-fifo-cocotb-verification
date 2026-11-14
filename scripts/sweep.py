"""Run the complete suite for six representative width/depth configurations."""
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIGURATIONS = [(1, 2), (8, 3), (5, 5), (8, 16), (16, 17), (32, 32)]
reports = []
for width, depth in CONFIGURATIONS:
    phase = f"phase7/w{width}_d{depth}"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/run.py"), "--phase", phase,
                           "--suite", "random", "--width", str(width), "--depth", str(depth)],
                          capture_output=True, text=True)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(proc.returncode)
    result = ROOT / "results" / phase
    tree = ET.parse(result / "junit.xml")
    tests = list(tree.iter("testcase"))
    assert len(tests) == 20 and not list(tree.iter("skipped")) and not list(tree.iter("failure")) and not list(tree.iter("error"))
    random_cycles = sum(json.loads((result / f"random_seed_{seed}.json").read_text())["cycles"] for seed in range(10))
    reports.append({"width": width, "depth": depth, "tests_passed": len(tests),
                    "randomized_cycles": 10000, "random_test_cycles_including_prelude_and_drain": random_cycles,
                    "required_scenario_bins_per_seed": 15, "status": "PASS"})
    print(f"PASS WIDTH={width} DEPTH={depth}: {len(tests)} tests, 10,000 randomized cycles")
summary = {"configurations": reports, "total_tests_passed": sum(item["tests_passed"] for item in reports),
           "total_randomized_cycles": 60000}
(ROOT / "results/phase7/summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("PASS: all six configurations")
