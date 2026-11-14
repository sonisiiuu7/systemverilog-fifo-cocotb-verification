# Verification plan

The testbench uses only public ports. A Python deque independently represents stored data; it does not inspect RTL pointers or memory. Acceptance is calculated from pre-edge model occupancy. Inputs are driven while clk is low; assertions run 5 ns after the rising edge, allowing nonblocking updates to settle. Every step checks dout, count, full, and empty, including idle/rejected-operation output hold behavior.

| Test | Requirement |
|---|---|
| basic | Reset and ordered transfers |
| reset_and_hold | Synchronous reset, priority, registered output hold |
| fill_drain | Capacity and ordered drain |
| overflow_protection | Rejected writes preserve queued data |
| underflow_protection | Rejected reads preserve state and output |
| boundaries | Simultaneous requests at empty/partial/full |
| streaming | Sustained simultaneous accepted transfers |
| wraparound | Repeated read/write pointer rollover |
| reset_during_traffic | Flush at partial/full occupancy; reset priority |
| data_patterns | Zero, ones, alternating and walking-one data |

Ten random tests use explicit seeds 0 through 9. Each includes a deterministic boundary prelude, 1,000 randomized cycles, and a final drain. Traffic alternates write-heavy, read-heavy, and balanced bursts with random reset injection. Each seed must hit all 15 required scenario bins (empty/partial/full, rejected read/write, simultaneous requests at each occupancy category, read/write wrap, nonempty reset, and all four request combinations). The deterministic prelude is included in the counters; they are not claimed as random-only coverage.

Coverage counters are functional scenario observations, not simulator code coverage. A wrap observation means DEPTH accepted operations since reset; ordering assertions verify the externally visible result. Logs and JUnit XML are stored per phase. CSV traces record sampled clock-edge behavior rather than continuous signal transitions.

## Parameter sweep

`scripts/sweep.py` runs all twenty tests for each configuration below, enforcing 15 scenario bins per seed each time:

| WIDTH | DEPTH | Purpose |
|---|---|---|
| 1 | 2 | Minimum supported width and depth |
| 8 | 3 | Small non-power-of-two depth |
| 5 | 5 | Non-byte width and non-power-of-two depth |
| 8 | 16 | Default baseline |
| 16 | 17 | Pointer rollover beyond a power-of-two boundary |
| 32 | 32 | Wider data and deeper buffer |

All six configurations passed locally: 120 test executions and 60,000 randomized cycles, plus boundary preludes and final drains. Other legal parameter values have not been exhaustively verified. CI repeats the sweep independently on Linux.
