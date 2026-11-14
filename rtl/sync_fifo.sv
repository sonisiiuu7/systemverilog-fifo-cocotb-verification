`timescale 1ns/1ps
module sync_fifo #(
    parameter integer WIDTH = 8,
    parameter integer DEPTH = 16,
    parameter integer COUNT_WIDTH = $clog2(DEPTH + 1)
) (
    input  logic                   clk,
    input  logic                   rst,
    input  logic                   wr_en,
    input  logic                   rd_en,
    input  logic [WIDTH-1:0]       din,
    output logic [WIDTH-1:0]       dout,
    output wire                    full,
    output wire                    empty,
    output logic [COUNT_WIDTH-1:0] count
);
    localparam integer PTR_WIDTH = (DEPTH <= 2) ? 1 : $clog2(DEPTH);
    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [PTR_WIDTH-1:0] wr_ptr, rd_ptr;
    wire write_accept = wr_en && !full;
    wire read_accept = rd_en && !empty;
    assign full = (count == DEPTH);
    assign empty = (count == 0);

    always_ff @(posedge clk) begin
        if (rst) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
            count <= 0;
            dout <= 0;
        end else begin
            if (write_accept) begin
                mem[wr_ptr] <= din;
                wr_ptr <= (wr_ptr == DEPTH-1) ? 0 : wr_ptr + 1'b1;
            end
            if (read_accept) begin
                dout <= mem[rd_ptr];
                rd_ptr <= (rd_ptr == DEPTH-1) ? 0 : rd_ptr + 1'b1;
            end
            case ({write_accept, read_accept})
                2'b10: count <= count + 1'b1;
                2'b01: count <= count - 1'b1;
                default: count <= count;
            endcase
        end
    end
endmodule
