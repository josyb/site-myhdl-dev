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