"""Plot sampled public-port values from the verified boundary test."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "results/phase5/restored/boundaries.csv").open()))
cycles = [int(row["cycle"]) for row in rows]
signals = ["wr_en", "rd_en", "write_accepted", "read_accepted", "count", "full", "empty", "dout"]
fig, axes = plt.subplots(len(signals), 1, figsize=(12, 9), sharex=True)
for axis, signal in zip(axes, signals):
    axis.step(cycles, [int(row[signal]) for row in rows], where="mid", linewidth=1.6)
    axis.set_ylabel(signal, rotation=0, ha="right", fontsize=9)
    axis.grid(alpha=0.25)
    axis.axvspan(0.5, 1.5, color="#f59e0b", alpha=0.16)
    axis.axvspan(17.5, 18.5, color="#ef4444", alpha=0.12)
axes[-1].set_xlabel("Checked clock cycle (post-edge samples)")
fig.suptitle("FIFO boundary behavior | WIDTH=8, DEPTH=16\nAmber: both requests at empty; red: both requests at full", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.94))
target = ROOT / "docs/images/boundary_trace.png"
target.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(target, dpi=150)
print(target)
