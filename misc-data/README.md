
## Detailed Spice Model (CDL) Generation

This is the procedure to generate detailed spice models of every standard cell including parasitics. 
They are generated using MAGIC. When running the script below, Magic loads the gds views of the "fd_sc_hd" standard cells and runs parasitic extraction. The extracted models are all combined into one cdl file.

*Note, this process will overwrite the existing cdl file in the pdk. (Although I am not sure if this file is being used for anything...)*

1. If you haven't already, install the PDK. Instructions [here](https://docs.google.com/document/d/1MK2YgaxSdSOQuAXPh7QiHsHKXvGz_htoxHYxVTlCMWc).
2. If you haven't already, install MAGIC.
3. Copy the tcl script `cdl_gen.tcl` to `<PDK_PATH>/libs.ref/sky130_fd_sc_hd/cdl`.
4. Navigate to this `cdl` directory.
5. (Rename `sky130_fd_sc_hd.cdl` if you want to save it.)
6. Run this command to invoke MAGIC and run the script:
    
    `<MAGIC_BIN> -dnull -noconsole -rcfile ../../../libs.tech/magic/sky130A.magicrc cdl_gen.tcl`
7. The resulting models are at `sky130_fd_sc_hd.cdl`
