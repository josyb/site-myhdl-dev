

The MEP112 should answer the following


   * What: what is being proposed, this should be evident early on:
     adding ND array support, currently only 1D list-of-signals is 
     support.
     
   * Why: because both Verilog and VHDL have this feature.
   
   * Models: different models and nomenclature:
      * Array of Signals
         * build like current list-of-signals but more dimension
         * myhdl.Array
      * Signal of myhdl.array
      * others
      
   * Implementation strategy 
      * flatten (most widely supported but different results)
      * convert to target HDL constructs with same support
   
     