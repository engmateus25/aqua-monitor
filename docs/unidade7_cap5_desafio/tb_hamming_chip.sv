// =============================================================================
// tb_hamming_chip.sv -- Testbench: HammingChip v1.0 (Golden Model)
// Unidade 7 | Capitulo 5 | PADIS
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// =============================================================================
`timescale 1ns/1ps

module tb_hamming_chip;

    logic [3:0] data_in;
    logic [6:0] encoded;
    logic [6:0] received;
    logic [3:0] data_out;
    logic [2:0] syndrome;
    logic       error_flag;

    int erros  = 0;
    int testes = 0;

    hamming_chip_top dut (.*);

    // Testa codificacao + decodificacao sem erro (round-trip)
    task automatic testa_roundtrip(input logic [3:0] din);
        data_in  = din;
        #2;
        received = encoded;    // transmite sem erro
        #2;
        testes++;
        if (data_out !== din || error_flag !== 1'b0) begin
            $display("  [FALHA-RT] data=%04b => enc=%07b => dec=%04b ErrFlag=%b",
                     din, encoded, data_out, error_flag);
            erros++;
        end else begin
            $display("  [OK-RT]   data=%04b => codeword=%07b => dec=%04b (sem erro)",
                     din, encoded, data_out);
        end
    endtask

    // Injeta erro em bit_pos e verifica correcao
    task automatic testa_correcao(input logic [3:0] din, input int bit_pos);
        data_in = din;
        #2;
        received = encoded ^ (7'b1 << bit_pos);  // injeta 1 erro
        #2;
        testes++;
        if (data_out !== din || error_flag !== 1'b1) begin
            $display("  [FALHA-ERR] data=%04b | bit=%0d | dec=%04b | syn=%03b | flag=%b",
                     din, bit_pos, data_out, syndrome, error_flag);
            erros++;
        end else begin
            $display("  [OK-ERR]  data=%04b | bit=%0d | syn=%03b=%0d | corrigido OK",
                     din, bit_pos, syndrome, syndrome);
        end
    endtask

    initial begin
        $dumpfile("dump_hamming.vcd");
        $dumpvars(0, tb_hamming_chip);

        $display("======================================================");
        $display(" HammingChip v1.0 -- Codec Hamming(7,4)");
        $display(" Simulacao Funcional (Golden Model)");
        $display(" Processo: CMOS 0.35um | VDD=3.3V");
        $display("======================================================");

        // Fase 1: Round-trip todos os 16 valores
        $display("\n--- Fase 1: Round-trip (16 vetores, sem erro) ---");
        testa_roundtrip(4'b0000); testa_roundtrip(4'b0001);
        testa_roundtrip(4'b0010); testa_roundtrip(4'b0011);
        testa_roundtrip(4'b0100); testa_roundtrip(4'b0101);
        testa_roundtrip(4'b0110); testa_roundtrip(4'b0111);
        testa_roundtrip(4'b1000); testa_roundtrip(4'b1001);
        testa_roundtrip(4'b1010); testa_roundtrip(4'b1011);
        testa_roundtrip(4'b1100); testa_roundtrip(4'b1101);
        testa_roundtrip(4'b1110); testa_roundtrip(4'b1111);

        // Fase 2: Correcao em todas as 7 posicoes (2 dados diferentes)
        $display("\n--- Fase 2: Correcao de erro em cada posicao (data=1011) ---");
        testa_correcao(4'b1011, 0); testa_correcao(4'b1011, 1);
        testa_correcao(4'b1011, 2); testa_correcao(4'b1011, 3);
        testa_correcao(4'b1011, 4); testa_correcao(4'b1011, 5);
        testa_correcao(4'b1011, 6);

        $display("\n--- Fase 2b: Correcao de erro em cada posicao (data=0101) ---");
        testa_correcao(4'b0101, 0); testa_correcao(4'b0101, 1);
        testa_correcao(4'b0101, 2); testa_correcao(4'b0101, 3);
        testa_correcao(4'b0101, 4); testa_correcao(4'b0101, 5);
        testa_correcao(4'b0101, 6);

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
