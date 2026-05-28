SIM             = icarus
TOPLEVEL_LANG   = verilog
VERILOG_SOURCES = $(PWD)/rtl/alu.sv
TOPLEVEL        = alu

COCOTB_TEST_MODULES = tb.tests.alu_test

export COCOTB_LOG_LEVEL = WARNING
export COCOTB_RESULTS_FILE = logs/results.xml

$(shell mkdir -p logs)
include $(shell cocotb-config --makefiles)/Makefile.sim