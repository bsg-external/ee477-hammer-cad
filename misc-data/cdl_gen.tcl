
# Load all standard cells
gds read ../gds/sky130_fd_sc_hd.gds;
set std_cell_prefix "sky130_fd_sc_hd"
set complete_cdl_file "sky130_fd_sc_hd.cdl"

# Initialize empty file
exec cat /dev/null > $complete_cdl_file

foreach name [lsearch -all -inline [cellname list allcells] $std_cell_prefix*] {
  # Load the cell
  load $name; 
  select top cell;
  set output_name "$name.cdl"

  # Extract 
  puts "extracting cell $name"
  extract do resistance;
  extract all;
  ext2sim labels on;
  ext2sim;
  extresist tolerance 10;
  extresist all;
  ext2spice lvs;
  ext2spice cthresh 0.1;
  ext2spice rthresh 10
  ext2spice extresist on;
  ext2spice -o $output_name;

  # Append to complete file
  exec cat $output_name >> $complete_cdl_file
}

exit
