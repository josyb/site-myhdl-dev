
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity mdarray_access is
  generic ( w : integer := 2 );
  port (
    clock : in std_logic;
    data_i : in unsigned(7 downto 0);
    wr : in std_logic;
    col : in unsigned(w downto 0);  -- address in 1D array (column)
    row : in unsigned(w downto 0);  -- row selection in 2D array
    slc : in unsigned(w downto 0);  -- square slice in 3D array
    data_o : out unsigned(7 downto 0)
    );
end entity mdarray_access;

architecture beh of mdarray_access is

  type cube is array (w downto 0, w downto 0, w downto 0) of unsigned(7 downto 0);
  signal mdarray : cube;
  signal data_ir : unsigned(7 downto 0);
  signal data_or : unsigned(7 downto 0);
  
  signal wr_r : std_logic;
  signal col_r : unsigned(w downto 0);
  signal row_r : unsigned(w downto 0);
  signal slc_r : unsigned(w downto 0);
begin
 
  process(clock)
    variable islc : integer;
    variable irow : integer;
    variable icol : integer;
  begin
    if (rising_edge(clock)) then
	   col_r <= col;
		row_r <= row;
		slc_r <= slc;
		data_ir <= data_i;
		
		icol := to_integer(col_r);
		irow := to_integer(row_r);
      islc := to_integer(slc_r);           
      if (wr = '1') then
        mdarray(islc, irow, icol) <= data_ir;
      end if;
		
      data_or <= mdarray(islc, irow, icol);
      data_o <= data_or;
    end if;   
  end process;  
  
end architecture beh; 
