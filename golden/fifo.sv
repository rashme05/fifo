`timescale 1ns/1ps

module fifo (
    input  logic       clk,
    input  logic       rst,
    input  logic       wr_en,
    input  logic       rd_en,
    input  logic [7:0] data_in,
    output logic [7:0] data_out,
    output logic       full,
    output logic       empty
);

    // Internal Signals
    logic [7:0] mem [0:3];
    logic [1:0] wr_ptr;
    logic [1:0] rd_ptr;
    logic [2:0] count;

    // Status Flags
    assign full  = (count == 4);
    assign empty = (count == 0);

    // Main FIFO Logic
    always_ff @(posedge clk) begin
        if (rst) begin
            wr_ptr   <= 0;
            rd_ptr   <= 0;
            count    <= 0;
            data_out <= 0;
        end else begin
            // Internal helper variables (local to this block)
            logic actual_wr;
            logic actual_rd;

            // Define logic: Write is allowed if not full, OR if we are reading while full
            actual_wr = wr_en && (!full || rd_en);
            // Define logic: Read is allowed only if not empty
            actual_rd = rd_en && !empty;

            // 1. Write Operation
            if (actual_wr) begin
                mem[wr_ptr] <= data_in;
                wr_ptr      <= wr_ptr + 1;
            end

            // 2. Read Operation
            if (actual_rd) begin
                data_out <= mem[rd_ptr];
                rd_ptr   <= rd_ptr + 1;
            end

            // 3. Counter Logic
            case ({actual_wr, actual_rd})
                2'b10: count <= count + 1; // Pure Write
                2'b01: count <= count - 1; // Pure Read
                default: count <= count;   // 11 (Both) or 00 (None)
            endcase
        end
    end

endmodule
