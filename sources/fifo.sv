`timescale 1ns/1ps

module fifo (
    input  logic clk,
    input  logic rst,
    input  logic wr_en,
    input  logic rd_en,
    input  logic [7:0] data_in,
    output logic [7:0] data_out,
    output logic full,
    output logic empty
);

logic [7:0] mem [0:3];
logic [1:0] wr_ptr;
logic [1:0] rd_ptr;
logic [2:0] count;

always_ff @(posedge clk) begin
    if (rst) begin
        wr_ptr <= 0;
        rd_ptr <= 0;
        count  <= 0;
        data_out <= 0;
    end
    else begin

        // write
        if (wr_en && !full) begin
            mem[wr_ptr] <= data_in;
            wr_ptr <= wr_ptr + 1;
            count <= count + 1;
        end

        // read
        if (rd_en && !empty) begin
            data_out <= mem[rd_ptr];
            rd_ptr <= rd_ptr + 1;
            count <= count - 1;
        end
        // counter update
	   if (wr_en && !full && !(rd_en && !empty))
    	    count <= count + 1;
	    else if (rd_en && !empty && !(wr_en && !full))
    	    count <= count - 1;
    end
end

assign full  = (count == 4);
assign empty = (count == 0);

endmodule
