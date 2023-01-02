# First, make sure you have set margains at least 212um for the core area of your design.
# Make sure there are no pin assignments for the pins you have io cells for


# Set SITE
set_db base_cell:sky130_ef_io__gpiov2_pad_wrapped .site sky130gpiov2site
set_db base_cell:sky130_ef_io__com_bus_slice_20um .site sky130gpiov2site
set_db base_cell:sky130_ef_io__com_bus_slice_10um .site sky130gpiov2site
set_db base_cell:sky130_ef_io__com_bus_slice_5um  .site sky130gpiov2site
set_db base_cell:sky130_ef_io__com_bus_slice_1um  .site sky130gpiov2site
# set_db base_cell:sky130_ef_io__corner_pad .site sky130gpiocorner
set_db base_cell:sky130_ef_io__corner_pad .site sky130gpiov2site
set_db base_cell:sky130_ef_io__corner_pad .class "pad_spacer"

# Create IO corner "rows"
create_io_row -site sky130gpiocorner -corner BL -name io_corner_BL
create_io_row -site sky130gpiocorner -corner BR -name io_corner_BR
create_io_row -site sky130gpiocorner -corner TL -name io_corner_TL
create_io_row -site sky130gpiocorner -corner TR -name io_corner_TR
# Fill corners
add_io_row_fillers -ignore_site_type -cells {sky130_ef_io__corner_pad} -filler_orient r180 -io_row io_corner_BL
add_io_row_fillers -ignore_site_type -cells {sky130_ef_io__corner_pad} -filler_orient r270 -io_row io_corner_BR
add_io_row_fillers -ignore_site_type -cells {sky130_ef_io__corner_pad} -filler_orient r90  -io_row io_corner_TL
add_io_row_fillers -ignore_site_type -cells {sky130_ef_io__corner_pad} -filler_orient r0   -io_row io_corner_TR

# Create IO rows
create_io_row -site sky130gpiov2site -side N -orient r0   -name io_row_N
create_io_row -site sky130gpiov2site -side S -orient r180 -name io_row_S
create_io_row -site sky130gpiov2site -side E -orient r270 -name io_row_E
create_io_row -site sky130gpiov2site -side W -orient r90  -name io_row_W

# create_io_row -derive_by_cells
# MANUALLY PLACE CELLS INSTEAD...

# After GPIOs have been arranged, enter these commands to add and fix fillers
# add_io_row_fillers -fill_any_gap -cells {sky130_ef_io__com_bus_slice_20um  sky130_ef_io__com_bus_slice_10um sky130_ef_io__com_bus_slice_5um sky130_ef_io__com_bus_slice_1um}
# set_db [get_db insts FILLER_io_*] .place_status fixed
