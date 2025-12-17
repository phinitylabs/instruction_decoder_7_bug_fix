import cocotb
from cocotb.triggers import Timer
import os
import random
from pathlib import Path
from cocotb_tools.runner import get_runner

# ------------------------------------------------------------
# Helper: check outputs
# ------------------------------------------------------------
async def check_outputs(dut, exp, label=""):
    await Timer(1, units="ns")

    for signal, expected in exp.items():
        actual = int(getattr(dut, signal).value)
        assert actual == expected, (
            f"{label}: {signal} expected {expected}, got {actual}"
        )


# ------------------------------------------------------------
# Test 0 – Decoder disabled when ID != 111
# ------------------------------------------------------------
@cocotb.test()
async def test_id_disable(dut):

    dut.id.value = 0b000     # not 111
    dut.instr_in.value = 0
    dut.cc_in.value = 0
    dut.instr_en.value = 0

    await Timer(2, units='ns')

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0, "stack_we":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":0, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0
    }

    await check_outputs(dut, expected, "ID != 111 → disabled")


# ------------------------------------------------------------
# Helper: run instruction with ID = 111
# ------------------------------------------------------------
async def run_instr(dut, instr, cc, en, expected, label):
    dut.id.value = 0b111
    dut.instr_in.value = instr
    dut.cc_in.value = cc
    dut.instr_en.value = en

    await Timer(2, units='ns')
    await check_outputs(dut, expected, label)


# ------------------------------------------------------------
# Instruction Tests
# ------------------------------------------------------------

# 1) Instruction Disable — 7'b0110101
@cocotb.test()
async def test_instruction_disable(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0, "stack_we":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0
    }

    await run_instr(
        dut,
        instr=0b01101,
        cc=0,
        en=1,
        expected=expected,
        label="Instruction Disable (0110101)"
    )


# 2) JSB PC + R — 7'b1101100
@cocotb.test()
async def test_jsb_pc_plus_r(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":1,
        "stack_re":0, "pop":0,
        "a_mux_sel":1, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b11011,
        cc=0,
        en=0,
        expected=expected,
        label="JSB PC + R (1101100)"
    )


# 3) Return S — 7'b1110000
@cocotb.test()
async def test_return_s(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":0,
        "stack_re":1, "pop":1,
        "a_mux_sel":2, "b_mux_sel":1,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b11100,
        cc=0,
        en=0,
        expected=expected,
        label="Return S (1110000)"
    )


# 4) Return S + D — 7'b1110100
@cocotb.test()
async def test_return_s_plus_d(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":1,
        "stack_re":1, "pop":1,
        "a_mux_sel":0, "b_mux_sel":1,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b11101,
        cc=0,
        en=0,
        expected=expected,
        label="Return S + D (1110100)"
    )


# 5) HOLD — 7'b1111000
@cocotb.test()
async def test_hold(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":1, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b11110,
        cc=0,
        en=0,
        expected=expected,
        label="HOLD (1111000)"
    )


# 6) SUSPEND — 7'b1111100
@cocotb.test()
async def test_suspend(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":0,
        "oen":0, "pc_mux_sel":1, "inc":0,
        "src_sel":0, "push":0, "stack_we":0
    }

    await run_instr(
        dut,
        instr=0b11111,
        cc=0,
        en=0,
        expected=expected,
        label="SUSPEND (1111100)"
    )

def test_instruction_decoder_7_hidden_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [proj_path / "sources/instruction_decoder_7.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="instruction_decoder_7",
        always=True,
    )
    runner.test(hdl_toplevel="instruction_decoder_7", test_module="test_instruction_decoder_7_hidden")
