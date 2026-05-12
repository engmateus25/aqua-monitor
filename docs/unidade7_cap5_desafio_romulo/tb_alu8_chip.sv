// =============================================================================
// tb_alu8_chip.sv -- Testbench: ALUChip v1.0
// Unidade 7 | Capitulo 5 | PADIS
// Autor : Romulo da Silva Lira
// =============================================================================
`timescale 1ns/1ps

module tb_alu8_chip;

    // Operacoes
    localparam OP_ADD = 3'b000;
    localparam OP_SUB = 3'b001;
    localparam OP_AND = 3'b010;
    localparam OP_OR  = 3'b011;
    localparam OP_XOR = 3'b100;
    localparam OP_NOT = 3'b101;
    localparam OP_SHL = 3'b110;
    localparam OP_SHR = 3'b111;

    logic [7:0] a, b;
    logic [2:0] op;
    logic [7:0] result;
    logic       flag_z, flag_c, flag_v, flag_n;

    int erros  = 0;
    int testes = 0;

    alu8_chip_top dut (.*);

    // -------------------------------------------------------------------------
    task automatic testa(
        input logic [7:0] ea, eb,
        input logic [2:0] eop,
        input logic [7:0] exp_result,
        input logic exp_z, exp_c, exp_v, exp_n,
        input string descricao
    );
        string op_str;
        case (eop)
            OP_ADD: op_str = "ADD";
            OP_SUB: op_str = "SUB";
            OP_AND: op_str = "AND";
            OP_OR:  op_str = "OR ";
            OP_XOR: op_str = "XOR";
            OP_NOT: op_str = "NOT";
            OP_SHL: op_str = "SHL";
            OP_SHR: op_str = "SHR";
            default: op_str = "???";
        endcase

        a = ea; b = eb; op = eop;
        #2;
        testes++;

        if (result !== exp_result || flag_z !== exp_z ||
            flag_c !== exp_c || flag_v !== exp_v || flag_n !== exp_n) begin
            $display("  [FALHA] %s %s | A=%02X B=%02X | res=%02X exp=%02X | Z%b C%b V%b N%b exp:Z%b C%b V%b N%b",
                op_str, descricao, ea, eb,
                result, exp_result,
                flag_z, flag_c, flag_v, flag_n,
                exp_z, exp_c, exp_v, exp_n);
            erros++;
        end else begin
            $display("  [OK] %s %s | %02Xh %s %02Xh = %02Xh | Z=%b C=%b V=%b N=%b",
                op_str, descricao, ea,
                (eop == OP_NOT || eop == OP_SHL || eop == OP_SHR) ? "  " :
                (eop == OP_ADD) ? "+" :
                (eop == OP_SUB) ? "-" :
                (eop == OP_AND) ? "&" :
                (eop == OP_OR)  ? "|" : "^",
                eb, result, flag_z, flag_c, flag_v, flag_n);
        end
    endtask

    // -------------------------------------------------------------------------
    initial begin
        $dumpfile("dump_alu.vcd");
        $dumpvars(0, tb_alu8_chip);

        $display("======================================================");
        $display(" ALUChip v1.0 -- ULA 8 bits (8 operacoes / 4 flags)");
        $display(" Simulacao Funcional");
        $display(" Processo: CMOS 0.35um | VDD=3.3V");
        $display("======================================================");

        // ----- ADD -----
        $display("\n--- ADD ---");
        testa(8'h03, 8'h05, OP_ADD, 8'h08, 0,0,0,0, "3+5=8");
        testa(8'hFF, 8'h01, OP_ADD, 8'h00, 1,1,0,0, "FF+01=00 (carry, zero)");
        testa(8'h7F, 8'h01, OP_ADD, 8'h80, 0,0,1,1, "7F+01=80 (overflow)");
        testa(8'h80, 8'h80, OP_ADD, 8'h00, 1,1,1,0, "80+80=00 (carry+overflow)");
        testa(8'hA0, 8'h30, OP_ADD, 8'hD0, 0,0,0,1, "A0+30=D0 (negativo)");

        // ----- SUB -----
        $display("\n--- SUB ---");
        testa(8'h08, 8'h03, OP_SUB, 8'h05, 0,1,0,0, "8-3=5");
        testa(8'h03, 8'h08, OP_SUB, 8'hFB, 0,0,0,1, "3-8=FB (negativo)");
        testa(8'h00, 8'h01, OP_SUB, 8'hFF, 0,0,0,1, "0-1=FF (borrow)");
        testa(8'h80, 8'h01, OP_SUB, 8'h7F, 0,1,1,0, "80-01=7F (overflow)");
        testa(8'h40, 8'h40, OP_SUB, 8'h00, 1,1,0,0, "40-40=00 (zero)");

        // ----- AND -----
        $display("\n--- AND ---");
        testa(8'hFF, 8'h0F, OP_AND, 8'h0F, 0,0,0,0, "FF&0F=0F");
        testa(8'hAA, 8'h55, OP_AND, 8'h00, 1,0,0,0, "AA&55=00 (zero)");
        testa(8'hF0, 8'hF0, OP_AND, 8'hF0, 0,0,0,1, "F0&F0=F0 (negativo)");

        // ----- OR -----
        $display("\n--- OR ---");
        testa(8'hAA, 8'h55, OP_OR,  8'hFF, 0,0,0,1, "AA|55=FF");
        testa(8'h00, 8'h00, OP_OR,  8'h00, 1,0,0,0, "00|00=00 (zero)");

        // ----- XOR -----
        $display("\n--- XOR ---");
        testa(8'hFF, 8'hFF, OP_XOR, 8'h00, 1,0,0,0, "FF^FF=00 (zero)");
        testa(8'hAA, 8'h55, OP_XOR, 8'hFF, 0,0,0,1, "AA^55=FF");
        testa(8'h3C, 8'h5A, OP_XOR, 8'h66, 0,0,0,0, "3C^5A=66");

        // ----- NOT -----
        $display("\n--- NOT ---");
        testa(8'h00, 8'hXX, OP_NOT, 8'hFF, 0,0,0,1, "~00=FF");
        testa(8'hFF, 8'hXX, OP_NOT, 8'h00, 1,0,0,0, "~FF=00 (zero)");
        testa(8'hA5, 8'hXX, OP_NOT, 8'h5A, 0,0,0,0, "~A5=5A");

        // ----- SHL -----
        $display("\n--- SHL ---");
        testa(8'h01, 8'hXX, OP_SHL, 8'h02, 0,0,0,0, "01<<1=02");
        testa(8'h80, 8'hXX, OP_SHL, 8'h00, 1,1,0,0, "80<<1=00 (carry+zero)");
        testa(8'h55, 8'hXX, OP_SHL, 8'hAA, 0,0,0,1, "55<<1=AA (negativo)");

        // ----- SHR -----
        $display("\n--- SHR ---");
        testa(8'h02, 8'hXX, OP_SHR, 8'h01, 0,0,0,0, "02>>1=01");
        testa(8'h01, 8'hXX, OP_SHR, 8'h00, 1,1,0,0, "01>>1=00 (carry+zero)");
        testa(8'hFF, 8'hXX, OP_SHR, 8'h7F, 0,1,0,0, "FF>>1=7F (carry)");

        $display("\n======================================================");
        $display(" Total: %0d/%0d testes corretos", testes-erros, testes);
        if (erros == 0)
            $display(">>> RESULTADO: APROVADO -- %0d/%0d testes passaram <<<",
                     testes, testes);
        else
            $display(">>> RESULTADO: REPROVADO -- %0d erro(s) <<<", erros);
        $display("=== Simulacao Concluida em %0t ===", $time);
        $finish;
    end

endmodule
