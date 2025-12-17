Instruction decoder is a fully combinational instruction-decoding block that receives a 5-bit opcode, a condition-code bit, and an instruction-enable signal, and produces all internal control signals for the microcode sequencer, stack subsystem, register subsystem, arithmetic datapath selectors, and program-counter steering logic.

The module outputs a valid set of outputs only when the identification value is 7.

When the module does not receive a valid identification code , the following behaviour is exhibited :

--> The output of the adder is 0. The carry input to the adder is discarded.

--> Stack is untouched.

--> The output of full adder is disabled.

--> The auxiliary register is disabled.

--> The auxiliary register mux selects the external data input.

--> The full adder value is held in the program counter.

--> The stack submodule receives the program counter value.

--> The result register holds its current value.

The list of valid instructions are as follows :

1. Instruction Disable 
-----------------------
Pattern: 0110101

--> The output of adder is 0. The carry input to the adder is discarded.

--> Stack is untouched.

--> The output of full adder is made available to result register.

--> The auxiliary register is disabled

--> The auxiliary register mux selects the external data input.

--> The full adder value is held in the program counter.

--> The stack submodule receives the program counter value.

--> The result register holds its current value.

Instruction 0 — JSB PC + R
---------------------------------------
Pattern: 1101100

--> The summation of program counter value and auxiliary register is routed to the output of full adder. The carry-input of the adder is considered.

--> The full adder value is selected and incremented at the program counter.

--> The output of the program counter is written into the stack location

--> The output of the full adder is made available to result register.

--> The auxiliary register is enabled to receive data from auxiliary register mux.

--> The auxiliary register mux selects the external data input.

--> The result register is deactivated


Instruction 2 — Return S
------------------------------
Pattern: 1110000

--> The data coming out from the stack is routed to the output of the full adder . The carry-input of the adder is not taken into account.

--> The output of the adder is selected for getting incremented in the program counter.

--> The auxiliary register mux selects the external data input.

--> The auxiliary register is activated.

--> The output of the full adder is made available to result register.

--> The result register holds its current value.

--> The stack submodule receives the content of the program counter


Instruction 3 — Return S + D
-----------------------------
Pattern: 1110100

--> The output of the adder is summation of data coming out from the stack and external data input. The carry-input of the adder is considered.

--> The output of the adder is selected for getting incremented in the program counter.

--> The auxiliary register mux selects the external data input.

--> The auxiliary register is activated.

--> The output of the full adder is made available to result register.

--> The result register holds its current value.

--> The stack submodule receives the content of the program counter


Instruction 4 — HOLD
-------------------------
Pattern: 1111000

--> The program counter value is routed to the output of full adder. The carry-input of the adder is not considered.

--> The program counter value is selected in program counter and not incremented.

--> The auxiliary register mux selects the external data input.

--> The auxiliary register is activated.

--> The output of the full adder is made available to result register.

--> The result register holds its current value.

--> The stack submodule receives the content of the program counter.

--> Stack is untouched.


Instruction 5 — SUSPEND
-------------------------
Pattern: 1111100

--> The program counter value is routed to the output of full adder. The carry-input of the adder is not considered.

--> The program counter value is selected at program counter and not incremented.

--> The auxiliary register mux selects the external data input.

--> The auxiliary register is activated.

--> The output of the full adder is not made available to result register.

--> The result register holds its current value.

--> The stack submodule receives the content of the program counter.

--> Stack is untouched.

I/O ports :
----------
Input ports :
---------------
id - 3-bit value to identify an instruction decoder instance.
instr_in - 5-bit opcode indicating the operation to be performed
cc_in - 1-bit code to determine whether a given instruction is unconditional or conditional. Its value is dont care for unconditional instructions.
instr_en - 1-bit active low signal to enable the execution of an instruction

Output ports:
-----------------
cen - 1-bit active high signal to enable the carry-input to full look-ahead adder
rst - 1-bit active high reset signal of stack pointer to initialize it to location 0 of stack RAM.
oen - 1-bit active high signal to enable the tristate buffer of full look-ahead adder
inc - 1-bit active high signal to enable the increment of the pc incrementer submodule
rsel - Signal to select the data at the auxiliary register mux submodule. It is used in combination with active low register enable signal to perform the selection. A value of 1 indicates to select full look-ahead adder output fedback from result register. A value of 0 indicates to select external data input.
rce - 1-bit active high signal to enable the auxiliary register submodule to transfer its input to output. It is used in combination with active low register enable signal to perform the operation.
pc_mux_sel - Signal to select the data at the pc submodule. A value of 1 is used for selecting the fedback program counter module data. A value of 0 is used for selecting the output of full look-aheadder output.
a_mux_sel - 2-bit signal to select the value of A-operand to full look-ahead adder. A value of 0 selects the external data input ; A value of 1 selects the output of auxiliary register ; A value of 2 selects constant 0.
b_mux_sel - 2-bit signal to select the value of B-operand to full look-ahead adder. A value of 0 selects the program counter submodule's data ; A value of 1 selects output of lifo stack submodule ; A value of 2 selects constant 0 ; A value of 3 selects the output of auxiliary register submodule.
push - 1-bit active high signal to perform increment of stack pointer
pop - 1-bit active high signal to perform decrement of stack pointer
src_sel - Signal to select the data at the lifo stack submodule. A value of 1 selects the external data input. A value of 0 selects the output of program counter submodule.
stack_we - 1-bit active high signal to write a selected data from the stack multiplexer submodule to write into a stack ram location
stack_re - 1-bit active high signal to read data from a selected stack ram location.
out_ce - 1-bit active high signal to enable the result register latch.

#Hints:
1. The 5-bit opcode , cc_in , instr_en bits have to be considered in the case expression to generate control signals. Considering any one of these alone to generate control signals is wrong.
2. Whenever full adder output is selected for getting incremented in the program counter pc_mux_sel must be 0. Whereas when the program counter value is selected for getting incremented pc_mux_sel must be 1.