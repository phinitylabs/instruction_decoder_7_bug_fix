import cocotb
from cocotb.triggers import Timer
import os
import random
from pathlib import Path
from cocotb_tools.runner import get_runner

# ------------------------------------------------------------
# Constants & Helpers
# ------------------------------------------------------------

# The "Disabled" or "Default" output state as per RTL and Spec
# (matches ID != 7 and case default)
EXPECTED_DEFAULT = {
    "rst": 0, "out_ce": 0, "rsel": 0, "rce": 0, "cen": 0,
    "stack_re": 0, "pop": 0, "stack_we": 0,
    "a_mux_sel": 2, "b_mux_sel": 2,
    "oen": 0, "pc_mux_sel": 0, "inc": 0,
    "src_sel": 0, "push": 0
}

# List of valid 7-bit patterns {instr_in, cc_in, instr_en} defined in RTL
# Used to skip known valid instructions when testing the 'default' case
VALID_PATTERNS = [
    0b0110101,  # Instr Disable
    0b1101100,  # JSB PC + R
    0b1110000,  # Return S
    0b1110100,  # Return S + D
    0b1111000,  # HOLD
    0b1111100   # SUSPEND
]

async def check_outputs(dut, exp, label=""):
    """Helper to compare DUT outputs against an expected dictionary."""
    await Timer(1, units="ns")
    
    # Iterate over expected items and assert equality
    for signal, expected in exp.items():
        actual = int(getattr(dut, signal).value)
        assert actual == expected, (
            f"{label}: {signal} expected {expected}, got {actual}"
        )

async def run_instr(dut, instr, cc, en, expected, label):
    """Helper to drive a specific valid instruction."""
    dut.id.value = 0b111
    dut.instr_in.value = instr
    dut.cc_in.value = cc
    dut.instr_en.value = en

    await Timer(2, units='ns')
    await check_outputs(dut, expected, label)


# ------------------------------------------------------------
# Robustness Test 1: ID Sweep (0-7)
# ------------------------------------------------------------
@cocotb.test()
async def test_id_mismatch_sweep(dut):
    """
    Verify that for any ID != 7 (0,1,2,3,4,5,6), the decoder is disabled
    regardless of the instruction inputs.
    """
    dut._log.info("Starting ID mismatch sweep...")

    for id_val in range(8):
        # Skip the valid ID (7) as that is covered by instruction tests
        if id_val == 7:
            continue

        dut.id.value = id_val
        
        # Test multiple random inputs for each invalid ID to ensure robustness
        for _ in range(5):
            rand_instr = random.randint(0, 31)
            rand_cc = random.randint(0, 1)
            rand_en = random.randint(0, 1)

            dut.instr_in.value = rand_instr
            dut.cc_in.value = rand_cc
            dut.instr_en.value = rand_en

            await Timer(2, units='ns')
            
            label = f"ID={id_val} (Mismatch) Input={rand_instr:05b}_{rand_cc}_{rand_en}"
            await check_outputs(dut, EXPECTED_DEFAULT, label)

# ------------------------------------------------------------
# Robustness Test 2: Undefined Instruction Sweep (Default Case)
# ------------------------------------------------------------
@cocotb.test()
async def test_undefined_instruction_sweep(dut):
    """
    Verify that even with Valid ID=7, any 7-bit instruction pattern 
    NOT in the valid list triggers the default (disabled) state.
    """
    dut._log.info("Starting Undefined Instruction (Default Case) sweep...")
    
    dut.id.value = 0b111  # Set Valid ID

    # Iterate through all possible 7-bit combinations (0 to 127)
    for pattern in range(128):
        
        # Skip if this pattern is actually a valid instruction
        if pattern in VALID_PATTERNS:
            continue

        # Decode pattern back to inputs for driving
        # Pattern structure: {instr_in[4:0], cc_in, instr_en}
        p_instr = (pattern >> 2) & 0x1F
        p_cc    = (pattern >> 1) & 0x1
        p_en    = pattern & 0x1

        dut.instr_in.value = p_instr
        dut.cc_in.value = p_cc
        dut.instr_en.value = p_en

        await Timer(2, units='ns')

        label = f"Valid ID, Invalid Pattern: {pattern:07b}"
        await check_outputs(dut, EXPECTED_DEFAULT, label)


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