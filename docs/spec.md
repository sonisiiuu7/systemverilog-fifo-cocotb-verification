# FIFO specification

Single-clock synchronous FIFO for digital-design and verification practice. This is an educational buffer, not a complete networking protocol implementation.

## Interface

| Signal | Direction | Meaning |
|---|---|---|
| clk | input | Rising-edge clock |
| rst | input | Active-high synchronous reset, highest priority |
| wr_en, rd_en | input | Write/read requests |
| din | input | WIDTH-bit write data |
| dout | output | WIDTH-bit registered read data |
| full, empty | output | Occupancy equals DEPTH / zero |
| count | output | Occupancy, width `$clog2(DEPTH+1)` |

Defaults: WIDTH=8, DEPTH=16. Supported WIDTH>=1, DEPTH>=2, including non-power-of-two depths. Pointers wrap explicitly at DEPTH-1.

## Clock-edge contract

Evaluate acceptance from the state immediately before the rising edge:

* read = rd_en AND NOT empty
* write = wr_en AND NOT full
* Reset overrides both operations: count, pointers, and dout become zero.
* Accepted writes append din; accepted reads remove the oldest item and update dout.
* dout holds its previous value if no read is accepted, including rejected reads.
* A reset does not clear memory; unread memory is invalid after reset.

| Pre-edge occupancy | Both requests asserted | Post-edge occupancy |
|---|---|---|
| Empty | Write only; no bypass | 1 |
| Partial | Read and write | Unchanged |
| Full | Read only; write rejected | DEPTH-1 |

This intentionally sacrifices a write opportunity at the full boundary to keep acceptance simple. No combinational fall-through, clock-domain crossing, packet parsing, or technology-specific memory primitive is provided.

## Acceptance criteria

Data and flags match an independent Python queue after every checked edge. Directed boundary tests, seeded randomized regressions, reset during traffic, and explicit pointer-wrap traffic must pass. Mutated RTL must fail a behavioral assertion. Test results demonstrate exercised scenarios, not formal correctness or measured HDL code coverage.
