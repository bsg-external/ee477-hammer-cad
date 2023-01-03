# Complex Digital VLSI System Design Labs
AKA: "VLSI II", EE 477, EE 525, CSE 567

Winter Quarter 2023

The labs for this course use the newly created ***Phoenix VLSI Flow***. 
This CAD flow is based on UCB-BAR's [Hammer](https://github.com/ucb-bar/hammer) VLSI flow.
The labs are divided into 4 modules (0-3) followed by a final project.

## Getting Started Links

* [Course Home Page](https://docs.google.com/document/d/1BVrtgQ0V3DoSF5G7i0n5ycWBMX-odDEENGdQuQx8Xk0/)
* [Linux Tutorial](https://web.csl.cornell.edu/courses/ece5745/handouts/ece5745-tut1-linux.pdf)
* [Git Tutorial](https://web.csl.cornell.edu/courses/ece5745/handouts/ece5745-tut2-git.pdf)

## Summary of Make Targets
Many of these targets also have a “redo” variant. By prepending “redo-” to the target, 
The same target will be run, but ignoring any changes to dependencies, and it will 
always run even if the output file is already up to date. For example, 
“make redo-sim-rtl” will re-run the RTL simulation again even if it was already completed.

| Build Commands | |
|----------------|-|
| `make sram`  | Runs BSG fakeram generator to create any SRAM macros. |
| `make syn` | Builds the design through synthesis. (Also has redo-* variant.) |
| `make par` | Builds the design through place-and-route. (Also has redo-* variant.) |
| `make par-to-floorplan` | Builds the design up through the floorplanning step of place-and-route. Then opens the Innovus GUI for the user to edit the floorplan. |
| `make par-from-floorplan` | Loads the design from the step after floorplanning (reads the “pre_place_bumps” database) and completes place-and-route.|
| `make drc` | Builds the design through place-and-route, if not already complete, then checks your design for DRC violations. (Also has redo-* variant.)|
| `make lvs` | Builds the design through place-and-route, if not already complete, then performs LVS circuit comparison. (Also has redo-* variant.)|
| `make ` (or `make all`) | Builds your design and runs both DRC and LVS checks. (Same behavior as “make drc lvs“)|

| Simulation Commands | |
|-------------------|-|
| `make sim-rtl` (or `make sim`) | Runs the RTL-level simulation of your testbench. |
| `make view-sim-rtl` | Opens the most recently run RTL simulation with DVE waveform viewer.|
| `make sim-rtl-hard` | Runs the RTL-level hardened-macro simulation of your testbench. |
| `make view-sim-rtl-hard` | Opens the most recently run RTL-hard simulation with DVE waveform viewer.|
| `make sim-syn` | Runs a gate-level simulation of your testbench using your post-synthesis netlist. This simulation includes timing annotation so each gate has its own delay.|
| `make sim-syn-functional` | Runs a gate-level simulation of your testbench using your post-synthesis netlist. This simulation leaves out any timing annotation.|
| `make view-sim-syn` | Opens the most recently run post-synthesis simulation with DVE waveform viewer.|
| `make sim-par` | Runs a gate-level simulation of your testbench using your post-place-and-route netlist. This simulation includes realistic timing annotation so each gate has its own delay.|
| `make sim-par-functional` | Runs a gate-level simulation of your testbench using your post-place-and-route netlist. This simulation leaves out any timing annotation.|
| `make view-sim-par` | Opens the most recently run post-place-and-route simulation with DVE waveform viewer.|

| Miscellaneous Commands | |
|-------------------|-|
| `make open-chip` | Opens the design in the Innovus GUI at the most recently built place-and-route step. |
| `make magic-open-chip` | Opens the completed chip design with MAGIC layout viewer. (A simple and lightweight GDS viewer. However the interface can be unintuitive for new-commers.)|
| `make clean-build` | Deletes all build and simulation data for the current design. *Be careful!* |
| `make install-tools` | Clones python libraries and scripts needed for Hammer. Just needs to be run once when setting up the build system.|
| `make clean-tools` | Removes the python libraries and scripts needed for Hammer.|

## Known Errors
For most steps, you will see many error messages. While many might be caused by you, some are
known to always happen and are safe to ignore. To make your debugging easier, here is a list
of known error messages that can generally be ignored:

### Build System (Hammer)
* **"ERROR installs  does not exist"**. An issue with how the PDK is imported.

### SRAM Generation (BSG Fakeram)
* 

### Synthesis (Genus)
* **"An object of type 'port|pin|hpin' named 'DEFAULT_CLOCK' could not be found."**: 
  Hammer usually generates an extra SDC file trying to create a clock on the pin 'DEFAULT_CLOCK'.
  This error, and a few following erros can be ignored. However if other SDC files cause errors, 
  you should look into those!

### Place-and-Route (Innovus)
* **"No pg_pin with name 'VNB' has been read in the cell"**: An issue with how several cells
  Are defined in the PDK. Can be ignored.
* **"create_clock: Invalid list of pins: 'DEFAULT_CLOCK'"**: Same issue seen by Genus when
  parsing clock constraints.
* **"Power net VPWR is not associated with any power domain."**: An issue with how several cells
  Are defined in the PDK. Can be ignored.
* **"Power net VPB is not associated with any power domain."**: An issue with how several cells
  Are defined in the PDK. Can be ignored.
* **"Genus executable not found in PATH."**: All the tools are run in seprate environments
  which is okay.
* **"Turning off Critical Region Resynthesis, which may impact final QOR."**: We currently
  don't use this feature, so not an issue.

### Simulation (VCS)
* **"Possible VERDI_HOME and VCS_HOME mismatch"**: All the tools are run in seprate
  environments which is okay.


### DRC (MAGIC)
* **"I/O possible"**: The first time MAGIC runs in a new environment, it puts out this 
  error and crashes for some reason... Try running again!
* **"Error while reading cell "\<NAME\>" (byte position \<NUM\>): Unknown layer/datatype in path,"**:
  Issue with the PDK.
* 

### LVS (MAGIC+Netgen)
* **"Error in SPICE file read: No file s8/V2.0.1/LVS/Calibre/source.cdl"**: This file 
  not needed by our flow, and doesn't exist.

### Formal (Conformal)
* TODO: