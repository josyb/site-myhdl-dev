-- comparing two diferent implementation of arrays in VHDL

-- this is the 'true' multi-dimensional type
-- 3D
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity arraynD is
	generic(w : integer := 2);
	port(
		clock  : in  std_logic;
		data_i : in  unsigned(7 downto 0);
		wr     : in  std_logic;
		col    : in  natural range 0 to w; -- address in 1D array (column)
		row    : in  natural range 0 to w; -- row selection in 2D array
		slc    : in  natural range 0 to w; -- square slice in 3D array
		data_o : out unsigned(7 downto 0)
	);
end entity arraynD;

architecture beh of arraynD is
	type cube is array (w downto 0, w downto 0, w downto 0) of unsigned(7 downto 0);
	signal mdarray : cube;

begin
	process(clock)
	begin
		if (rising_edge(clock)) then
			if (wr = '1') then
				mdarray(slc, row, col) <= data_i;
			end if;

			data_o <= mdarray(slc, row, col);
		end if;
	end process;

end architecture beh;

-- here we 'stack' 1D arrays
-- 1D x 1D x 1D
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity arraym1D is
	generic(
		w : integer := 2
	);
	port(
		clock  : in  std_logic;
		data_i : in  unsigned(7 downto 0);
		wr     : in  std_logic;
		col    : in  natural range 0 to w; -- address in 1D array (column)
		row    : in  natural range 0 to w; -- row selection in 2D array
		slc    : in  natural range 0 to w; -- square slice in 3D array
		data_o : out unsigned(7 downto 0)
	);
end entity arraym1D;

architecture beh of arraym1D is
	type cols is array (w downto 0) of unsigned(7 downto 0);
	type rows is array (w downto 0) of cols;
	type planes is array (w downto 0) of rows;
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

end architecture beh;

-- comparing both

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity arrays is
	generic(
		w : integer := 2
	);
	port(
		clock   : in  std_logic;
		data_i  : in  unsigned(7 downto 0);
		wr      : in  std_logic;
		col     : in  natural range 0 to w; -- address in 1D array (column)
		row     : in  natural range 0 to w; -- row selection in 2D array
		slc     : in  natural range 0 to w; -- square slice in 3D array
		col2    : in  natural range 0 to w; -- address in 1D array (column)
		row2    : in  natural range 0 to w; -- row selection in 2D array
		slc2    : in  natural range 0 to w; -- square slice in 3D array
		data_o  : out unsigned(7 downto 0);
		data2_o : out unsigned(7 downto 0)
	);
end entity arrays;

architecture beh of arrays is
begin
	nD : entity work.arraynD
		generic map(
			w => w
		)
		port map(
			clock  => clock,
			data_i => data_i,
			wr     => wr,
			col    => col,
			row    => row,
			slc    => slc,
			data_o => data_o
		);

	m1D : entity work.arraym1D
		generic map(
			w => w
		)
		port map(
			clock  => clock,
			data_i => data_i,
			wr     => wr,
			col    => col2,
			row    => row2,
			slc    => slc2,
			data_o => data2_o
		);
end architecture beh; 
