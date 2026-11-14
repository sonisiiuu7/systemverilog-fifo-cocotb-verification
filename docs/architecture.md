# Architecture and Python walkthrough

## RTL state

* `mem`: DEPTH words of WIDTH bits. Only accepted writes update it.
* `wr_ptr`: location for the next accepted write.
* `rd_ptr`: location of the oldest queued word.
* `count`: number of valid words, ranging from zero through DEPTH inclusive.
* `dout`: registered output; holds the last read value until another accepted read or reset.

Pointers explicitly wrap at DEPTH-1, so non-power-of-two depths work. Pointer width is at least one bit. Count needs `$clog2(DEPTH+1)` bits because it must represent the full capacity, not just a memory address. Do not override COUNT_WIDTH; it is derived from DEPTH.

On a rising edge, reset clears pointers, count, and output. Otherwise, each accepted operation updates its pointer and relevant data. A two-bit case statement updates count once: +1 for write-only, -1 for read-only, unchanged for both or neither. Nonblocking assignments make all operations use the pre-edge state.

## Why the Python model is independent

The reference uses `collections.deque`, not another circular buffer. It therefore does not reproduce the RTL's pointer implementation. Before each edge, acceptance is computed from deque length. An accepted read removes the front; an accepted write appends the new value. The expected output persists between reads. Reset clears the queue and expected output.

The testbench drives inputs with clock low, waits 5 ns, raises the clock, then waits 5 ns for registered and combinational outputs to settle. It compares four observable outputs after every step. This deliberate schedule avoids sampling before nonblocking assignments complete. The separate synchronous-reset check asserts reset between edges and verifies that occupancy does not change early.

## Small example

For DEPTH=2, write A then B: count is 2 and full is asserted. Request read and write C simultaneously. The pre-edge FIFO is full, so the write is rejected; dout becomes A and count becomes 1. A later read returns B. C must never appear. This boundary behavior is specified, not an accidental implementation detail.

## Files to read in order

1. `docs/spec.md`: the behavioral contract.
2. `rtl/sync_fifo.sv`: pointers, storage, and occupancy.
3. `tb/test_fifo.py`: Scoreboard.step, then basic and boundaries.
4. The randomized test: explicit seeds, traffic bias, and scenario gates.
5. `scripts/mutate.py`: how faulty RTL is tested without editing production code.

## Safe exercises

Change a random seed, add a long idle interval, or add another supported width/depth combination. To change full-boundary throughput, first revise the specification and reference model, then RTL and directed tests. Do not silently change one side of the contract.
