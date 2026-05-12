// =============================================================================
// tb_moore.sv -- Testbench para sequence_detector_moore
// Unidade 5 | Capitulo 2 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// =============================================================================
`timescale 1ns/1ps

module tb_moore;

    // -------------------------------------------------------------------------
    // Sinais
    // -------------------------------------------------------------------------
    logic clk;
    logic rst_n;
    logic x;
    logic sequence_detected;

    // Contador de erros para relatorio automatico PASS/FAIL
    int erros = 0;
    int acertos = 0;

    // -------------------------------------------------------------------------
    // Instanciacao do DUT
    // -------------------------------------------------------------------------
    sequence_detector_moore dut (
        .clk               (clk),
        .rst_n             (rst_n),
        .x                 (x),
        .sequence_detected (sequence_detected)
    );

    // -------------------------------------------------------------------------
    // Clock: periodo de 10 ns (50 MHz)
    // -------------------------------------------------------------------------
    initial clk = 0;
    always #5 clk = ~clk;

    // -------------------------------------------------------------------------
    // Tarefa auxiliar: aplica bit, aguarda borda e verifica saida
    // -------------------------------------------------------------------------
    task automatic aplica_bit(
        input logic bit_in,
        input logic esperado,
        input int   ciclo
    );
        x = bit_in;
        @(posedge clk);
        #1; // pequeno atraso apos borda para ler saida estabilizada
        if (sequence_detected !== esperado) begin
            $display("  [FALHA] Ciclo %0d | x=%b | detected=%b | Esperado=%b",
                     ciclo, bit_in, sequence_detected, esperado);
            erros++;
        end else begin
            $display("  [OK]    Ciclo %0d | x=%b | detected=%b | Esperado=%b",
                     ciclo, bit_in, sequence_detected, esperado);
            acertos++;
        end
    endtask

    // -------------------------------------------------------------------------
    // Estimulos e verificacao
    // Sequencia de teste: "11010010111"
    // Bits: 1 1 0 1 0 0 1 0 1 1 1
    // Ciclo: 1 2 3 4 5 6 7 8 9 10 11
    // Deteccao Moore esperada:
    //   Estado GOT101 atingido em ciclo 4 (seq. 1[1]0[1] -- posicoes 2,3,4)
    //   Estado GOT101 atingido em ciclo 9 (seq. [1]0[1]  -- posicoes 7,8,9)
    //   Ciclo 11: bit='1', estado transita de GOT1, saida=0
    // -------------------------------------------------------------------------
    initial begin
        $dumpfile("dump_moore.vcd");
        $dumpvars(0, tb_moore);

        // Reset inicial
        rst_n = 0;
        x     = 0;
        @(posedge clk);
        #1;
        rst_n = 1;

        $display("=== Simulacao Moore FSM -- Detector de Sequencia '101' ===");
        $display("Sequencia de entrada: 1 1 0 1 0 0 1 0 1 1 1");
        $display("%-10s  %-6s  %-12s  %-12s  %-8s",
                 "Ciclo", "x", "detected", "Esperado", "Status");
        $display("%s", {72{"─"}});

        //              bit  esperado  ciclo
        aplica_bit(1'b1,  1'b0,  1);   // GOT1,   saida=0
        aplica_bit(1'b1,  1'b0,  2);   // GOT1,   saida=0
        aplica_bit(1'b0,  1'b0,  3);   // GOT10,  saida=0
        aplica_bit(1'b1,  1'b1,  4);   // GOT101, saida=1 <- DETECCAO
        aplica_bit(1'b0,  1'b0,  5);   // GOT10,  saida=0 (sobreposicao)
        aplica_bit(1'b0,  1'b0,  6);   // IDLE,   saida=0
        aplica_bit(1'b1,  1'b0,  7);   // GOT1,   saida=0
        aplica_bit(1'b0,  1'b0,  8);   // GOT10,  saida=0
        aplica_bit(1'b1,  1'b1,  9);   // GOT101, saida=1 <- DETECCAO
        aplica_bit(1'b1,  1'b0, 10);   // GOT1,   saida=0 (sobreposicao)
        aplica_bit(1'b1,  1'b0, 11);   // GOT1,   saida=0

        $display("%s", {72{"─"}});
        $display("Acertos: %0d/11 | Erros: %0d", acertos, erros);
        if (erros == 0)
            $display(">>> RESULTADO: APROVADO -- 11/11 ciclos corretos <<<");
        else
            $display(">>> RESULTADO: REPROVADO -- %0d erro(s) detectado(s) <<<", erros);

        $display("=== Simulacao Concluida em %0t ===", $time);
        $finish;
    end

endmodule
