import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def clocked_register(dut):
    for value in [0, 1, 0, 1]:
        dut.clk.value = 0
        dut.d.value = value
        await Timer(5, unit="ns")
        dut.clk.value = 1
        await Timer(5, unit="ns")
        assert int(dut.q.value) == value
