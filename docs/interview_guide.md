# Interview preparation

## A concise project explanation

"I worked on a parameterized synchronous FIFO in SystemVerilog and verified it with Python/cocotb. An independent deque scoreboard checks data ordering, occupancy, and status flags after every clock edge. Directed tests cover boundaries and resets; seeded random traffic exercises mixed operations. Deliberate RTL mutations demonstrate that the tests detect specific errors."

Explain your own contribution accurately and mention AI assistance when discussing how the project was developed. Do not claim UVM, synthesis, timing closure, or formal verification work from this repository.

## Questions to practice

| Question | Key point |
|---|---|
| Why a FIFO? | Decouples producers and consumers while preserving order |
| Why an occupancy counter? | Distinguishes full from empty even when pointer addresses coincide |
| Why nonblocking assignments? | Clocked updates use old state and take effect together |
| Why reject writes at full with a simultaneous read? | Explicit simple contract; higher throughput would require a revised design |
| Why not reset the memory array? | Resetting validity state makes old contents inaccessible |
| How do non-power-of-two depths wrap? | Explicit compare with DEPTH-1, not natural binary overflow |
| How does Python avoid repeating an RTL bug? | Deque ordering instead of implementing circular pointers again |
| Why seeded randomness? | Reproduce exact traffic and failing cycle |
| What does coverage mean here? | Fifteen defined scenario bins, not HDL line/toggle coverage |
| What can passing simulation not prove? | All possible traces, physical timing, and silicon behavior |
| How did you validate the tests? | Three isolated RTL mutations cause behavioral assertion failures |

## Demonstration sequence

Run the directed suite; show the boundary trace; explain the empty/full simultaneous cases. Run the random suite and inspect a seed's coverage JSON. Run mutation checks and explain one assertion. Finally, change WIDTH/DEPTH and rerun. Be able to predict the expected count before reading the result.

## Resume wording after you understand and reproduce the work

"Implemented and verified a parameterized synchronous FIFO using SystemVerilog and Python/cocotb, with a deque scoreboard, directed boundary tests, seeded random traffic, and deliberate fault-injection checks."

Add numerical test/configuration counts only from the results you personally reproduced.
