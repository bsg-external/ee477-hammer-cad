// Wrapper for sky130_ef_io__gpiov2_pad_wrapped GPIO cells.
// Connects PAD directly to DATA_IN (exposed to core area).
// This is the simplist configuration to get data onto the chip.

module gpio_analog_input 
  (inout PAD
  ,output DATA_IN
  ,inout AMUXBUS_A
  ,inout AMUXBUS_B
  );

  // Hardcode GPIO to use analog input moe
  // sky130_ef_io__gpiov2_pad gpio_ain (
  sky130_ef_io__gpiov2_pad_wrapped gpio_ain (
     .PAD(PAD) // Pad connection
    ,.IN_H() // TODO: no doc on this...
    ,.PAD_A_NOESD_H(DATA_IN) // Direct connection to pad
    ,.PAD_A_ESD_0_H() // Connect to pad with ESD (has resistance)
    ,.PAD_A_ESD_1_H() // Connect to pad with ESD (has resistance)
    ,.DM(3'b000) // Drive Mode: 000='in and out buffers disabled', 001='Input buffers only'
    ,.HLD_H_N(1'b1) // Not input Hold (active low) (1= never hold)
    ,.IN() // Input into the core area TODO: connect?
    ,.INP_DIS(1'b0) // Input Disable (acvite high)
    ,.IB_MODE_SEL(1'b0) // Used select between VDDIO and VCCHIB based thresholds (0=VDDIO, 1=VCCHIB)
    ,.ENABLE_H(1'b1) // GPIO Global Enable (Should be 0 when cell is being configured)
    ,.ENABLE_VDDA_H(1'b1) // Enable on GPIO analog section
    ,.ENABLE_INP_H(1'b0) // Setting for input signal when enable_h is '0'
    ,.OE_N(1'b1) // Output Not Enable (active high)
    ,.TIE_HI_ESD() // '1' I think...
    ,.TIE_LO_ESD() // '0' I think...
    ,.SLOW(1'b0) // Output edge rate control (0=faster, 1=slower)
    ,.VTRIP_SEL(1'b0) // Buffer trip point (0=CMOS, 1=LVTTL)
    ,.HLD_OVR(1'b0) // Hold overwrite signal (overwrites hld_h_n)
    ,.ANALOG_EN(1'b0) // Enables analog input mode
    ,.ANALOG_SEL(1'b0) // Selects amuxmux: (0=amuxbus_a, 1=amuxbus_b)
    ,.ANALOG_POL(1'b0) // Sets analog function
    ,.ENABLE_VDDIO(1'b1) 
    ,.ENABLE_VSWITCH_H(1'b1)    
    ,.OUT(1'b0) // Output from the core area (zero for now)
    ,.AMUXBUS_A(AMUXBUS_A)
    ,.AMUXBUS_B(AMUXBUS_B)
    // VSSA, VDDA, VSWITCH, VDDIO_Q, VCCHIB, VDDIO, VCCD, VSSIO, VSSD, VSSIO_Q 
    );
  
endmodule