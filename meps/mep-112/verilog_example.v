

module mdarray_access
#( parameter w = 2 )
(
  input  wire  clock,

  input  wire  [w:0] col,
  input  wire  [w:0] row,
  input  wire  [w:0] slc,

  input  wire  [7:0] data_i,
  input  wire  wr,
  output reg   [7:0] data_o,
  output reg   [7:0] data_m
 );

  // 128*128*128*256 = 536Mbits
  reg [7:0] mdarray [w:0][w:0][w:0];
  reg [7:0] data_d;

  always @(posedge clock) begin
    if (wr == 1'b1) begin
      mdarray[slc][row][col] <= data_i;
    end
    data_d <= mdarray[slc][row][col];
    data_o <= data_d;
  end

  // 128*128*128*256 = 536Mbits
  localparam N  = 4*4*4;
  reg [7:0] mem [N-1:0];
  integer   addr;
  always @(posedge clock) begin
    addr = slc*row*col;
    if (wr == 1'b1) begin
      mem[addr] <= data_i;
    end
    data_m <= mem[addr];
  end
  
endmodule
                      
