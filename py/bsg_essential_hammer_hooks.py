'''
This file is for Hammer tool hooks essential to run on the UW ECE servers.
These should probably always be added as hooks in this environment. 
However, they are not considdered generic enough to warrent a pull request 
to the Hammer (or Hammer plugin) repos.
'''

import os, stat
from tokenize import maybe

import hammer_vlsi
from hammer_vlsi import CLIDriver, HammerToolHookAction, HierarchicalMode
import hammer_tech

from typing import Dict, Callable, Optional, List
from pathlib import Path

# COMMON HOOKS ################################################################

def test_hook(x: hammer_vlsi.HammerTool) -> bool:
    '''Just an example hook. Shows how to get a hammer config variable.'''
    data = x.get_setting('sim.inputs.top_module')
    print(f'\n##### HOOK TEST: SIM TOP MODULE IS "{data}". #####\n')
    return True

def magic_read_macro_lefs(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Prepend commands to a tcl script: Read LEF files for SRAM macros.
    (This is DEPRECEATED, and should no longer be required.)
    
    Where to use: 
        pre_insertion_hook for the 'init_design' step of Magic DRC tool.        
        pre_insertion_hook for the 'run_ext2spice' step of Netgen LVS tool.
    '''
    lef_files = x.technology.read_libs([hammer_tech.filters.lef_filter], hammer_tech.HammerTechnologyUtils.to_plain_item)
    macro_lefs = []
    # Only load LEF files from SRAM macros
    macros_names = [s['name'] for s in x.get_setting('vlsi.inputs.sram_parameters')]
    for f in lef_files:
        if Path(f).stem in macros_names:
            macro_lefs.append(f)
    # Load LEFs at the start of the Magic extraction script 
    x.append('# Reading LEFs')
    for f in macro_lefs:
        x.append(f'lef read {f}')
    x.append('')
    return True

# SYNTHESIS HOOKS #############################################################

def genus_syn_with_preserve(x: hammer_vlsi.HammerTool) -> bool:
    '''
    If any modules in the preserve_modules list, set the 'preserve' property on them. 
    Then run synthesis.
    
    Where to use:
        replacement_hook for the 'syn_generic' step of Genus synthesis tool.
    '''
    try: preserve_mods = x.get_setting('synthesis.inputs.preserve_modules')
    except: 
        x.verbose_append('syn_generic')
        return True # Return if variable is not set
    for mod in preserve_mods:
        if mod == x.top_module: # Top level is preserved
            x.verbose_append(f'set_db designs:{x.top_module} .preserve true')
            x.set_setting('synthesis.syn_map', False) # Don't map in this case
        else: # A sub-module is preserved
            x.verbose_append(f'set_db module:{x.top_module}/{mod} .preserve true')
    x.verbose_append('syn_generic')
    return True

def genus_maybe_syn_map(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Check the syn_map setting. If set false, skip mapping. This is usually true 
    if all modules have the 'preserve' property set.
    
    Where to use:
        replacement_hook for the 'syn_map' step of Genus synthesis tool.
    '''
    try: map = x.get_setting('synthesis.syn_map')
    except: map = True # If variable not set, then do map
    if map: x.verbose_append("syn_map") 
    # Need to suffix modules for hierarchical simulation if not top
    if x.hierarchical_mode not in [HierarchicalMode.Flat, HierarchicalMode.Top]:
        x.verbose_append("update_names -module -log hier_updated_names.log -suffix _{MODULE}".format(MODULE=x.top_module))
    return True

# PAR HOOKS ###################################################################

def innovus_overwrite_write_sdf_funct(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Overwrite the write_sdf() function in the Innovus tool plugin.
    Add extra arguments to the 'write_sdf' tcl command.
    
    Where to use:
        pre_insertion_hook for the 'write_design' Innovus PAR step.
    '''
    def write_sdf(self) -> bool:
        '''Write SDF like before, but with extra arguments'''
        if self.hierarchical_mode.is_nonleaf_hierarchical():
            self.verbose_append("flatten_ilm")
        # Output the Standard Delay Format File for use in timing annotated gate level simulations
        self.verbose_append("write_sdf {run_dir}/{top}.par.sdf -recompute_delaycal -edges library -min_period_edges posedge".format(
            run_dir=self.run_dir, top=self.top_module))
        return True
    type(x).write_sdf = write_sdf # Overwrite function for the entire class
    return True

def innovus_snap_floorplan(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Run the 'snap_floorplan' command. This snaps automatically placed 
    macros to the manufacturing grid. (which doesn't happen by default 
    for some reason...)

    Where to use:
        post_insertion_hook for the 'place_opt_design' Innovus PAR step.
    '''
    x.verbose_append("snap_floorplan -all")
    return True

def innovus_extra_reports(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Generate additional final reports: power, area, timing by path group.
    Not strictly required, but helpful.
    
    Where to use:
        pre_insertion_hook for the 'write_design' Innovus PAR step.
    '''
    x.verbose_append(f'report_power -hierarchy all -out_file {x.top_module}_power.rpt')
    x.verbose_append(f'report_area -detail > {x.top_module}_area.rpt')
    # Generate timing reports by path group
    x.append('set pg_list [get_path_group -include_internal_groups]')
    x.append('set_db timing_enable_simultaneous_setup_hold_mode true')
    x.append( 'foreach_in_collection g $pg_list {')
    x.append(f'  report_timing -check_type setup -group [get_property $g name] -nworst 50 > timingReports/{x.top_module}_postRoute_[get_property $g name].tarpt.gz')
    x.append(f'  report_timing -check_type  hold -group [get_property $g name] -nworst 50 > timingReports/{x.top_module}_postRoute_[get_property $g name]_hold.tarpt.gz')
    x.append( '}')
    return True

# SIMULATION HOOKS ############################################################

def vcs_gen_dve_script(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Generate a waveform viewing script for DVE.
    
    Where to use:
        pre_insertion_hook for the 'run_simulation' VCS simulation step.
    '''
    lic = x.get_setting('synopsys.SNPSLMD_LICENSE_FILE')
    rdir = x.run_dir
    vcs_home = x.get_setting('sim.vcs.vcs_home')
    os.makedirs(rdir+'/generated_scripts', exist_ok=True)
    fout_name = rdir+'/generated_scripts/run_dve'
    with open(fout_name, 'w') as fout:
        fout.write(f'#!/bin/bash\n')
        fout.write(f'export LM_LICENSE_FILE={lic}\n')
        fout.write(f'export VCS_HOME={vcs_home}\n')
        fout.write(f'{vcs_home}/bin/dve -mode64 -logdir {rdir} -vpd {rdir}/vcdplus.vpd\n')
    os.chmod(fout_name, os.stat(fout_name).st_mode | stat.S_IEXEC)
    x.logger.info(f'DVE script "{fout_name}" written.')
    return True

def vcs_remove_input_file_duplicates(x: hammer_vlsi.HammerTool) -> bool:
    '''
    Remove duplicate files from the input file list (Fixes some VCS issues)
    
    Where to use:
        pre_insertion_hook for the 'run_vcs' VCS simulaiton step.
    '''
    result = []
    [result.append(ele) for ele in x.input_files if ele not in result]
    x.input_files = result
    return True
