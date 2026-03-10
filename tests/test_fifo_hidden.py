from __future__ import annotations
import os
from pathlib import Path
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb_tools.runner import get_runner

@cocotb.test()
async def fifo_full_verification(dut):

    """Enhanced Test to catch simultaneous Read/Write bugs"""

    # Clock
    clock = Clock(dut.clk, 10, unit="ns")

    cocotb.start_soon(clock.start())

    # Reset
    dut.rst.value = 1
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.data_in.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    await RisingEdge(dut.clk)

    # ---------------------------
    # TEST 1: Fill FIFO
    # ---------------------------

    for i in range(4):
        dut.data_in.value = i + 10
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)

    dut.wr_en.value = 0
    await RisingEdge(dut.clk)
    assert int(dut.full.value) == 1, "FIFO should be FULL after 4 writes"

    # ---------------------------
    # TEST 2: Simultaneous R/W
    # ---------------------------

    dut.rd_en.value = 1
    dut.wr_en.value = 1
    dut.data_in.value = 99

    await RisingEdge(dut.clk)
    await Timer(1, "ps") 

    actual_out = int(dut.data_out.value)
    print(f"DEBUG: data_out is {actual_out}") 
    # FIX: Added closing quote and parenthesis
    assert actual_out == 10, f"Expected 10, got {actual_out}"

    # ---------------------------
    # TEST 3: Drain FIFO
    # ---------------------------
    # IMPORTANT: Ensure wr_en is dropped before the next clock
    dut.wr_en.value = 0
    dut.rd_en.value = 1

    # Remaining values in FIFO: [11, 12, 13] + the [99] we just wrote
    expected_values = [11, 12, 13, 99]

    for expected in expected_values:
        await RisingEdge(dut.clk)
        await Timer(1, "ps") 
        
        actual = int(dut.data_out.value)
        print(f"DRAIN DEBUG: Expected {expected}, Got {actual}")
        assert actual == expected, f"Expected {expected}, got {actual}"

    # Final check
    await RisingEdge(dut.clk)
    assert int(dut.empty.value) == 1, "FIFO should be EMPTY"

def test_fifo4_hidden_runner():

    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent


    # BUGGY RTL

    # sources = [proj_path / "sources/fifo4.sv"]
    # GOLDEN RTL

    sources = [proj_path / "sources/fifo.sv"]
    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel="fifo",
        always=True,
    )

    runner.test(
        hdl_toplevel="fifo",
        test_module="test_fifo_hidden",
    )

