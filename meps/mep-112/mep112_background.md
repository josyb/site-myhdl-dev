
---
mep: 112 Background  
title: VHDL and Verilog Multidimensional Arrays  
layout: mep   
authors: Christohper Felton, Josy Boelen  
status: Draft  
date: 2015-07-30  
---  

 
VHDL and Verilog Multidimensional Support
=========================================
  
The following is a review of the VHDL and Verilog *Nd array* support.
This is intended to be a review to determine if one of the existing 
models should be used and a survey of the target language support.
 

VHDL Arrays
-----------
VHDL has many abstraction tools and multidimensional arrays has
existed in VHDL from the beginning.

### VHDL Multidimensional Example
The following is a variant of a multidimensional array example
extracted from [vhdl_example.vhd]().  This example demonstrates 
how multidimensional arrays can be created in VHDL. 
    
```vhdl
  type t_cube is array (3 downto 0, 3 downto 0, 3 downto 0) of unsigned(31 downto 0);
  signal mdarray : t_cube;  

-- accessing the array
process begin
    -- ...
    if (wr = '1') then
      mdarray(islc, irow, icol) <= data_i;
    else
      data_o <= mdarray(islc, irow, icol);
    end if; 
end
```

#### Synthesis results

| Tool |logic |registers |BRAM |Pins |Fmax|
| ---- |----- |--------- |---- |---- |----|
| A    |1024  |2080      |0    |73   |220 |

**Note** no RAM was inferred, as the coding style doesn't match the 
inference template. The example shown may mislead you that RAM inference was 
anticipated.  But this multi-dimensional array allows for both accessing and 
updating all elements at the same time, which is totaly different than a RAM 
where we typically can only access one location at a time. A good example is 
[convolution](http://docs.gimp.org/en/plug-in-convmatrix.html) where a  a 3 x 3 
matrix is used.


### Another VHDL Multidimensional Example
Another way to declare a multidimensional array is to declare subtypes iteratively:
```VHDL
	type cols   is array (3 downto 0) of unsigned(31 downto 0);
	type rows   is array (3 downto 0) of cols;
	type planes is array (3 downto 0) of rows;
	signal tcube : planes;

begin
	process(clock)
	begin
		if (rising_edge(clock)) then
			if (wr = '1') then
				tcube(slc)(row)(col) <= data_i;
			end if;

			data_o <= tcube(slc)(row)(col);
		end if;
	end process;
```
###  Comparing the two different implementations
#### At the VHDL Level
The _true_ 3D type,
```VHDL
type t_cube is array (2 downto 0, 2 downto 0, 2 downto 0) of unsigned(31 downto 0)
``` 
can be seen as a cube, depicted in this picture:   

![3 * 3 * 3 objects](./cube-matrix-cropped.png)

The _nD_-type can be easily used as a module port because the _fully unconstrained_ type 
declaration ```type cube is array (natural range <>, natural range <>, natural range <>) 
of unsigned; -- VHDL2008!``` can be declared in a _general_ VHDL _package_. 
But updating (assigning a new value to) each element must be done atomically, e.g.:

```VHDL
type t_col  is array (2 downto 0) of unsigned(31 downto 0)
type t_cube is array (2 downto 0, 2 downto 0, 2 downto 0) of unsigned(31 downto 0)
signal ndarray : t_cube;
signal col : t_col;

-- updating the row 0 of plane 0
ndarray( 0, 0 ) <= col ; 				-- error, missing lowest index for ndarray
ndarray( 0, 0, 2 downto 0 ) <= col ; 	-- illegal, (type mismatch)

for i in 0 to 2 loop
	ndarray(0,0,i) <= col(i) ; 			-- correct
end loop ;
```
    

In contrast the _stacked_ 1D x 1D x 1D type 
```VHDL
type cols   is array (2 downto 0) of unsigned(31 downto 0);
type rows   is array (2 downto 0) of cols;
type planes is array (2 downto 0) of rows;
```
has a rather flat representation.  The picture show how we get to an eventual 
1Dx1Dx1D of _object_

![3 * (3 * (3 objects))](./expanded-stacked_1D-hor.png)

Note that we stacked the objects horizontally and vertically in an alternating 
manner. This way we can easily show even more than 3 dimensions.  Accessing a 
_stacked_ m1D type is a lot more versatile, as
```VHDL
type cols   is array (2 downto 0) of unsigned(31 downto 0);
type rows   is array (2 downto 0) of cols;
type planes is array (2 downto 0) of rows;
signal tcube : planes;
signal row   : rows;
signal col   : cols;

tcube(0)(0) <= col ;   -- valid
tcube(1)    <= row ;   -- valid
tcube(2)(1) <= row(2); -- valid
```

#### At the RTL Level
At least in Quartus II, after Analysis and Synthesis, there is **no difference** 
between the RTL Schematics!  


Verilog Arrays
--------------
In the Verilog 2001 standard (1394-2001) multi-dimensional arrays
were added [reference].  Even though multi-dimensional array support
was added in Verilog 2001 it did not support multi-dimensional array
ports.  The Prior to this multi-dimensional arrays 
were not supported and many open-source Verilog simulators still
do not support multi-dimensional arrays [reference].  Although there
is limited support in the open-source tools the 2001 standard is 
over 10 years old and commonly used by many developers.

### Verilog Multidimensional Example

```verilog
module m1Dcube
(
	input we, clk,
	input [1:0] a2, a1, a0,
	input [31:0] data, 
	output reg [31:0] q 
	);
	
	reg [31:0] cube[3:0][3:0][3:0]; // # words = 1 << address width
	integer l, k, j;
	
	always @(posedge clk)
	begin
		// writing
		if ( we )
			cube[a2][a1][a0] <= data;
		// reading						
		q <= cube[a2][a1][a0];
	end
endmodule
```

#### Synthesis results

| Tool       |logic |registers |BRAM |Pins |Fmax|
| ---------- |----- |--------- |---- |---- |----|
| A 15.0 C4E |1442  |2080      |0    |72   |233 |

<!-- include synthesis results for vhdl and verilog -->
