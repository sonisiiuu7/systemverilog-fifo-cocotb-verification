"""Check release documentation links and recorded passing baseline evidence."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
broken = []
count = 0
for doc in [ROOT / "README.md", *(ROOT / "docs").rglob("*.md")]:
    for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "#")):
            continue
        count += 1
        if not (doc.parent / target.split("#")[0]).exists():
            broken.append(f"{doc.relative_to(ROOT)}: {target}")
assert not broken, f"Broken documentation links: {broken}"
result = ROOT / "results/phase6"
tree = ET.parse(result / "junit.xml")
tests = list(tree.iter("testcase"))
assert len(tests) == 20 and not list(tree.iter("failure")) and not list(tree.iter("error")) and not list(tree.iter("skipped"))
metadata = json.loads((result / "run.json").read_text())
assert metadata["exit_code"] == 0
assert metadata["source_sha256"] == hashlib.sha256((ROOT / "rtl/sync_fifo.sv").read_bytes()).hexdigest()
mutations = json.loads((ROOT / "results/phase5/mutation_summary.json").read_text())
assert len(mutations) == 3 and all(item["detected"] for item in mutations)
report = {"status": "PASS", "local_documentation_links_checked": count,
          "baseline_tests_passed": len(tests), "mutations_detected": len(mutations),
          "rtl_hash_matches_tested_source": True}
(result / "release_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
