"""Black-box, cycle-accurate checks against an independent deque model."""
from collections import Counter, deque
import csv
import json
import os
from pathlib import Path

import cocotb
from cocotb.triggers import Timer

WIDTH = int(os.environ["FIFO_WIDTH"])
DEPTH = int(os.environ["FIFO_DEPTH"])
SUITE = os.environ["FIFO_SUITE"]
RESULTS = Path(os.environ["FIFO_RESULTS"])


class Scoreboard:
    def __init__(self, dut, name):
        self.dut = dut
        self.name = name
        self.queue = deque()
        self.output = 0
        self.cycle = 0
        self.coverage = Counter()
        self.rows = []
        self.writes = self.reads = 0

    async def step(self, wr=0, rd=0, data=0, rst=0):
        d = self.dut
        before = len(self.queue)
        data &= (1 << WIDTH) - 1
        write = bool(wr and before < DEPTH and not rst)
        read = bool(rd and before > 0 and not rst)
        d.clk.value = 0
        d.rst.value = rst
        d.wr_en.value = wr
        d.rd_en.value = rd
        d.din.value = data
        await Timer(5, unit="ns")
        if rst:
            self.coverage["reset_nonempty" if before else "reset_empty"] += 1
            self.queue.clear()
            self.output = 0
            self.writes = self.reads = 0
        else:
            self.coverage[f"pre_{'empty' if before == 0 else 'full' if before == DEPTH else 'partial'}"] += 1
            self.coverage[f"request_{int(bool(wr))}{int(bool(rd))}"] += 1
            if wr and not write:
                self.coverage["rejected_write"] += 1
            if rd and not read:
                self.coverage["rejected_read"] += 1
            if wr and rd:
                self.coverage[f"both_{'empty' if before == 0 else 'full' if before == DEPTH else 'partial'}"] += 1
            if read:
                self.output = self.queue.popleft()
                self.reads += 1
                self.coverage["accepted_read"] += 1
                if self.reads % DEPTH == 0:
                    self.coverage["read_wrap"] += 1
            if write:
                self.queue.append(data)
                self.writes += 1
                self.coverage["accepted_write"] += 1
                if self.writes % DEPTH == 0:
                    self.coverage["write_wrap"] += 1
        d.clk.value = 1
        # Advance past nonblocking assignments and combinational flag updates.
        await Timer(5, unit="ns")
        actual = {key: int(getattr(d, key).value) for key in ["dout", "count", "full", "empty"]}
        expected = {"dout": self.output, "count": len(self.queue),
                    "full": int(len(self.queue) == DEPTH), "empty": int(not self.queue)}
        context = f"{self.name} cycle={self.cycle} pre_count={before} wr={wr} rd={rd} rst={rst}"
        for key in expected:
            assert actual[key] == expected[key], f"{context}: {key} actual={actual[key]} expected={expected[key]}"
        self.rows.append({"cycle": self.cycle, "rst": rst, "wr_en": wr, "rd_en": rd,
                          "din": data, **actual, "write_accepted": int(write), "read_accepted": int(read)})
        self.cycle += 1

    def save(self):
        (RESULTS / f"{self.name}.json").write_text(json.dumps({"cycles": self.cycle, "coverage": dict(self.coverage)}, indent=2) + "\n")
        if self.name == "basic" or self.name == "boundaries":
            with (RESULTS / f"{self.name}.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=self.rows[0].keys())
                writer.writeheader()
                writer.writerows(self.rows)


@cocotb.test()
async def basic(dut):
    s = Scoreboard(dut, "basic")
    await s.step(rst=1)
    for value in range(min(3, DEPTH)):
        await s.step(wr=1, data=value + 17)
    for _ in range(min(3, DEPTH)):
        await s.step(rd=1)
    await s.step()
    s.save()
