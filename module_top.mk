# Top level make file to be included by lab Makefiles

TOP_DIR ?= .
BASEJUMP_STL_PATH ?= $(TOP_DIR)/../basejump_stl

# Add environment variables for Hammer.
export HAMMER_HOME =$(TOP_DIR)/hammer
export HAMMER_VLSI =$(HAMMER_HOME)/src/hammer-vlsi
export PYTHONPATH +=:$(HAMMER_HOME)/src:$(HAMMER_HOME)/src/jsonschema:$(HAMMER_HOME)/src/python-jsonschema-objects:$(HAMMER_HOME)/src/hammer-tech:$(HAMMER_HOME)/src/hammer-vlsi
export MYPYPATH    =$(PYTHONPATH)
export PATH       +=:$(HAMMER_HOME)/src/hammer-shell

# GENERATED BUILD SYSTEM ######################################################

INPUT_CFGS  :=$(OBJ_DIR)/paths.yml $(TOP_DIR)/hammer_cfg_top.yml $(INPUT_CFGS)
#SOURCE_CFGS ?=DEFAULT
TB_CFGS     ?=DEFAULT

# If this is running in the University of Washington ECE labs, source the common environment file.
ifneq ($(findstring ece.uw.edu, $(shell hostname)),)
	HAMMER_ENV ?= /home/projects/ee477.2026wtr/cad/hammer_env.yml
else 
	HAMMER_ENV ?= $(TOP_DIR)/hammer_env_default.yml
endif

HAMMER_EXEC ?=$(TOP_DIR)/hammer_run

OBJ_DIR ?= DEFAULT
SRAM_CFG ?= $(OBJ_DIR)/sram_generator-rundir/sram_generator-output.json

HAMMER_EXTRA_ARGS := $(foreach x,$(SRAM_CFG), -p $(x)) $(HAMMER_EXTRA_ARGS) -l hammer.log
SIM_EXTRA_ARGS    ?= $(foreach x,$(TB_CFGS),  -p $(x))

HAMMER_SIM_RTL_DEPENDENCIES+=$(SRAM_CFG)
HAMMER_SYN_DEPENDENCIES+=$(SRAM_CFG)

# Make build directory, or do nothing if it already exists
$(OBJ_DIR):
	mkdir $@ || :

# Generate extra config file
$(OBJ_DIR)/paths.yml: | $(OBJ_DIR)
	echo "bsg_root: $(realpath $(BASEJUMP_STL_PATH))" > $@
	echo "vlsi.core.local_tool_path: $(realpath $(TOP_DIR))" >> $@

$(OBJ_DIR)/hammer.d: $(OBJ_DIR)/paths.yml | $(TOP_DIR)/hammer
	$(HAMMER_EXEC) -e $(HAMMER_ENV) $(foreach x,$(INPUT_CFGS), -p $(x)) \
		-l hammer.log --obj_dir $(OBJ_DIR) build
	# Scott: disable sim targets in the generated hammer.d makefile. These
	# targets will be implemented by the hammer-bsg-plugins/vcs-mk included
	# below.
	sed -i '/^sim-/ s/^/#/' $@
	sed -i '/^redo-sim-/,+1 s/^/#/' $@

# Include generated makefile
include $(OBJ_DIR)/hammer.d
include $(TOP_DIR)/hammer-bsg-plugins/vcs-mk/include.mk
include $(TOP_DIR)/hammer-bsg-plugins/klayout-mk/include.mk

# SRAM generation target
.PHONY: sram
sram: $(SRAM_CFG)
$(SRAM_CFG): $(INPUT_CFGS)
	$(HAMMER_EXEC) -e $(HAMMER_ENV) $(foreach x,$(INPUT_CFGS), -p $(x)) -l hammer.log \
		-o $@ --obj_dir $(OBJ_DIR) sram-generator

# Default simulation to RTL sim
.PHONY: sim redo-sim
sim: sim-rtl
redo-sim: redo-sim-rtl

# Default target: build everything
.DEFAULT_GOAL := all
.PHONY: all
all: drc lvs

# MISC TARGETS ################################################################

# Delete all generated data
.PHONY: clean-build
clean-build:
	rm -rfv $(OBJ_DIR)
	rm -v hammer.log

# Run PAR only through floorplan. Then open the floorplanning GUI.
par-to-floorplan: HAMMER_EXTRA_ARGS +=--to_step floorplan_design
par-to-floorplan: $(abspath $(OBJ_DIR)/par-input.json)
	make redo-par HAMMER_EXTRA_ARGS="$(HAMMER_EXTRA_ARGS)"
	make open-chip

# Run PAR only after floorplan. 
par-from-floorplan: HAMMER_EXTRA_ARGS +=--after_step floorplan_design
par-from-floorplan: 
	make redo-par HAMMER_EXTRA_ARGS="$(HAMMER_EXTRA_ARGS)"

# Open Innovus GUI with built design
open-chip: $(OBJ_DIR)/par-rundir/generated-scripts/open_chip
	$<

# Open Magic GUI and load the built design
magic-open-chip: $(OBJ_DIR)/par-rundir/generated-scripts/magic_open_chip
	$<

# Open Klayout GUI and load the built design
klayout-open-chip: $(OBJ_DIR)/par-rundir/generated-scripts/klayout_open_chip
	$<

