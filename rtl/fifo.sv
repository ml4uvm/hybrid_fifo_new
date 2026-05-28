module fifo #(
    parameter DATA_WIDTH = 8,
    parameter DEPTH = 8
)(
    input  logic clk,
    input  logic rst,

    input  logic write_en,
    input  logic read_en,
    input  logic [DATA_WIDTH-1:0] data_in,

    output logic [DATA_WIDTH-1:0] data_out,
    output logic full,
    output logic empty
);

    // ----------------------------
    // Internal signals
    // ----------------------------
    localparam ADDR_WIDTH = $clog2(DEPTH);

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    logic [ADDR_WIDTH-1:0] wr_ptr, rd_ptr;
    logic [ADDR_WIDTH:0] count;  // can go up to DEPTH

    // ----------------------------
    // Status flags
    // ----------------------------
    assign full  = (count == DEPTH);
    assign empty = (count == 0);

    // ----------------------------
    // Sequential logic
    // ----------------------------
    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            wr_ptr  <= 0;
            rd_ptr  <= 0;
            count   <= 0;
            data_out <= 0;
        end else begin

            // WRITE
            if (write_en && !full) begin
                mem[wr_ptr] <= data_in;
                wr_ptr <= wr_ptr + 1;
            end

            // READ
            if (read_en && !empty) begin
                data_out <= mem[rd_ptr];
                rd_ptr <= rd_ptr + 1;
            end

            // COUNT UPDATE
            case ({write_en && !full, read_en && !empty})
                2'b10: count <= count + 1; // write only
                2'b01: count <= count - 1; // read only
                2'b11: count <= count;     // simultaneous
                default: count <= count;
            endcase

        end
    end

endmodule