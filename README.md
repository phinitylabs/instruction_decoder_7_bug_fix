# Instruction Decoder 7 Bug Fix

This is a Verilog RTL debug task for HUD evaluation framework.

## Problem Description

The instruction decoder module has a bug that causes simulation failures with random input combinations. The task is to debug and fix the RTL implementation.

## Structure

- `sources/` - RTL source files
- `tests/` - Test files (cocotb-based)
- `docs/` - Specification documentation
- `prompt.txt` - Task description

## Branches

- `instruction_decoder_7_baseline` - Broken implementation (starting point for agents)
- `instruction_decoder_7_test` - Test suite with hidden tests
- `instruction_decoder_7_golden` - Correct implementation (reference solution)

