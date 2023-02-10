'''
This file is for hammer hooks specific to the EE-477 Modules.
'''

import json
import os, stat
from tokenize import maybe

import hammer_vlsi
from hammer_vlsi import CLIDriver, HammerToolHookAction, HierarchicalMode
import hammer_tech
from hammer_tech import Library, ExtraLibrary

from typing import Dict, Callable, Optional, List
from pathlib import Path

def fakeram_gen_macro_swaps(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Generate a verilog Library which uses the BSG hard macro swapping system to swap out generated SRAMs.
    Any SRAM dimensions specified in the Hammer config files will swapped. This covers instances of:
    * bsg_mem_1rw_sync
    * bsg_mem_1rw_sync_mask_write_bit
    * bsg_mem_1rw_sync_mask_write_byte
    
    Where to use:
        post_insertion_hook for the 'register_macros' BSG Fakeram SRAM generator step.
    '''
    # If no srams, do nothing
    if not len(x.input_parameters):
        return True    
    bsg_root = x.get_setting('bsg_root')
    swap_gen_script_path = f'{bsg_root}/hard/common/bsg_mem/bsg_mem_generator.py'
    # Create generated verilog output directory
    out_dir = os.path.join(x.run_dir, 'generated_v')
    try: os.mkdir(out_dir)
    except: pass
    # Write config file for hard swap file generator: 'bsg_mem_generator'
    swap_gen_dict = {'memories':[]}
    for p in x.input_parameters:
        swap_gen_dict['memories'].append({'ports':'1rw', 'mux':1, 'type':'1sram', 'width':p.width, 'depth':p.depth})
    swap_gen_cfg = os.path.join(x.run_dir, 'swap_gen_cfg.json')
    with open(swap_gen_cfg, 'w') as fout: fout.write(json.dumps(swap_gen_dict, indent=2))
    # Combine all generated hard swap files
    hard_swap_v_name = os.path.join(out_dir, 'bsg_mem_1rw_sync_all.v')
    # Add verilog header files from BSG repo (Contains verilog macros) for 3 types of rams (no write mask, bit write mask, byte write mask)
    os.system(f'cat {bsg_root}/hard/fakeram/bsg_mem_1rw_sync_macros.vh                  > {hard_swap_v_name}')
    os.system(f'cat {bsg_root}/hard/fakeram/bsg_mem_1rw_sync_mask_write_bit_macros.vh  >> {hard_swap_v_name}')
    os.system(f'cat {bsg_root}/hard/fakeram/bsg_mem_1rw_sync_mask_write_byte_macros.vh >> {hard_swap_v_name}')
    # Generate and concatinate hard swap files for all 3 types of rams. Must use Python 2! :(
    os.system(f'python2 {swap_gen_script_path} {swap_gen_cfg} 1rw 0                    >> {hard_swap_v_name}')
    os.system(f'python2 {swap_gen_script_path} {swap_gen_cfg} 1rw 1                    >> {hard_swap_v_name}')
    os.system(f'python2 {swap_gen_script_path} {swap_gen_cfg} 1rw 8                    >> {hard_swap_v_name}')
    # Create library for hard swap verilog file. Use it for both synthesis and simulation
    x.output_libraries.append(ExtraLibrary(
        prefix=None, library=Library(
            name='macro_hard_swap', verilog_synth=hard_swap_v_name, verilog_sim=hard_swap_v_name
        )
    ))
    return True

# PAR HOOKS ###################################################################

def innovus_gen_magic_view_script(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Generate a script to open the output GDS in MAGIC.
    
    Where to use:
        post_insertion_hook for the 'write_design' Innovus PAR step.
    '''
    bash_script = os.path.join(x.generated_scripts_dir, 'magic_open_chip')
    magic_bin = x.get_setting('drc.magic.magic_bin')
    magic_rc = x.get_setting('drc.magic.rcfile')
    os.makedirs(x.generated_scripts_dir, exist_ok=True)
    with open(bash_script, 'w') as fout:
        fout.write('#!/bin/bash\n')
        fout.write(f'{magic_bin} -d XR -rcfile {magic_rc} {x.output_gds_filename} &\n')
        fout.write('echo \necho "### MAGIC launched in the background."\n')
        fout.write(f'echo "### Once the GDS has loaded, enter the command \'load {x.top_module}\' to view the top level cell."\n')
        fout.write('echo \n')
    os.chmod(bash_script, 0o755)
    x.logger.info('MAGIC chip viewer script generated.')
    return True

def innovus_gen_klayout_view_script(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Generate a script to open the output GDS in Klayout. Requires manual path to Ruby libraries.
    
    Where to use:
        post_insertion_hook for the 'write_design' Innovus PAR step.
    '''
    bash_script = os.path.join(x.generated_scripts_dir, 'klayout_open_chip')
    klayout_bin = x.get_setting('klayout.klayout_bin')
    ruby_lib = x.get_setting('klayout.ruby_lib')
    layer_prop = x.get_setting('klayout.layer_properties')
    with open(bash_script, 'w') as fout:
        fout.write('#!/bin/bash\n')
        fout.write(f'export RUBYLIB={ruby_lib};\n')
        fout.write(f'{klayout_bin} -l {layer_prop} {x.output_gds_filename} &\n')
    os.chmod(bash_script, 0o755)
    x.logger.info('Klayout chip viewer script generated.')
    return True

# FORMAL HOOKS ################################################################

def conformal_remove_mem_src(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Remove bsg_mem_1rw* source files for formal verification. This is required because we need
    the generated versions of these files in order to swap out for fakeram macro instances.

    Where to use:
        pre_insertion_hook for the 'setup_designs' Conformal step.
    '''
    x.reference_files = [s for s in x.reference_files if not s.endswith('bsg_mem_1rw_sync.v')]
    x.reference_files = [s for s in x.reference_files if not s.endswith('bsg_mem_1rw_sync_mask_write_bit.v')]
    x.reference_files = [s for s in x.reference_files if not s.endswith('bsg_mem_1rw_sync_mask_write_byte.v')]
    return True

# SIMULATION HOOKS ############################################################

def vcs_gen_trace_roms(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Generates trace ROM verilog files from the list of trace files (.tr).
    
    Where to use:
        pre_insertion_step for the 'run_vcs' VCS simulation step.
    '''
    # Get trace files
    try: trace_files = x.get_setting('sim.inputs.trace_files')
    except: trace_files = []
    if not len(trace_files):
        x.logger.info('No trace files found, no trace roms will be generated.')
        return True # Return if no trace files listed
    # Get ROM generation script
    rom_gen_script = os.path.join(x.get_setting('bsg_root'), 'bsg_mem', 'bsg_ascii_to_rom.py')
    # Set up output directory
    out_dir = os.path.join(x.run_dir, 'generated_v')
    try: os.mkdir(out_dir)
    except: pass
    # Generate each file
    for t in trace_files:
        fout = os.path.join(out_dir, Path(t).stem+'_rom.v')
        open(fout, 'w').write(x.run_executable([rom_gen_script, t, Path(fout).stem]))
        x.input_files.append(fout) # Append to simulation sources
    return True