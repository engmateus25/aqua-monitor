// =============================================================================
// tb_mealy.sv -- Testbench para sequence_detector_mealy
// Unidade 5 | Capitulo 2 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// =============================================================================
// NOTA IMPORTANTE DE TIMING:
//   Na FSM de Mealy a saida e combinacional (depende de estado + entrada).
//   Diferente da Moore (saida valida apos posedge), a saida Mealy e valida
//   DURANTE o ciclo de clock, antes da proxima borda de subida.
//   Por isso este testbench amostra sequence_detected ANTES do posedge.
// =============================================================================
`timescale 1ns/1ps

module tb_mealy;

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
    sequence_detector_mealy dut (
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
    // Tarefa auxiliar Mealy:
    //   1. Aplica bit logo apos o posedge anterior (estado ja registrado)
    //   2. Aguarda estabilizacao combinacional (#3 ns)
    //   3. Amostra saida ANTES da proxima borda (Mealy: saida valida aqui)
    //   4. Avanca ao proximo posedge para registrar transicao de estado
    // -------------------------------------------------------------------------
    task automatic aplica_bit(
        input logic bit_in,
        input logic esperado,
        input int   ciclo
    );
        x = bit_in;
        #3;  // aguarda estabilizacao logica combinacional
        if (sequence_detected !== esperado) begin
            $display("  [FALHA] Ciclo %0d | x=%b | detected=%b | Esperado=%b",
                     ciclo, bit_in, sequence_detected, esperado);
            erros++;
        end else begin
            $display("  [OK]    Ciclo %0d | x=%b | detected=%b | Esperado=%b",
                     ciclo, bit_in, sequence_detected, esperado);
            acertos++;
        end
        @(posedge clk);  // avanca ao proximo posedge (registra next_state)
        #1;
    endtask

    // -------------------------------------------------------------------------
    // Estimulos e verificacao
    // Sequencia de teste: "11010010111"
    // Bits: 1 1 0 1 0 0 1 0 1 1 1
    // Ciclo: 1 2 3 4 5 6 7 8 9 10 11
    //
    // Deteccao Mealy (saida combinacional durante o ciclo):
    //   Ciclo 4: estado=GOT10, x=1 -> detected=1 (sequencia "101" completa)
    //   Ciclo 9: estado=GOT10, x=1 -> detected=1 (segunda deteccao)
    //   Todos os demais ciclos: detected=0
    // -------------------------------------------------------------------------
    initial begin
        $dumpfile("dump_mealy.vcd");
        $dumpvars(0, tb_mealy);

        // Reset inicial (assincrono, ativo baixo)
        rst_n = 0;
        x     = 0;
        @(posedge clk);
        #1;
        rst_n = 1;

        $display("=== Simulacao Mealy FSM -- Detector de Sequencia '101' ===");
        $display("Sequencia de entrada: 1 1 0 1 0 0 1 0 1 1 1");
        $display("Timing: saida amostrada ANTES do posedge (saida combinacional Mealy)");
        $display("%-10s  %-6s  %-12s  %-12s  %-8s",
                 "Ciclo", "x", "detected", "Esperado", "Status");
        $display("%s", {72{"─"}});

        //              bit  esperado  ciclo
        // Estado inicial: IDLE
        aplica_bit(1'b1,  1'b0,  1);   // IDLE + x=1 -> detected=(IDLE==GOT10)&&1=0
        aplica_bit(1'b1,  1'b0,  2);   // GOT1 + x=1 -> detected=(GOT1==GOT10)&&1=0
        aplica_bit(1'b0,  1'b0,  3);   // GOT1 + x=0 -> detected=(GOT1==GOT10)&&0=0
        aplica_bit(1'b1,  1'b1,  4);   // GOT10+ x=1 -> detected=1 <- DETECCAO
        aplica_bit(1'b0,  1'b0,  5);   // GOT1 + x=0 -> detected=(GOT1==GOT10)&&0=0
        aplica_bit(1'b0,  1'b0,  6);   // GOT10+ x=0 -> detected=(GOT10==GOT10)&&0=0
        aplica_bit(1'b1,  1'b0,  7);   // IDLE + x=1 -> detected=(IDLE==GOT10)&&1=0
        aplica_bit(1'b0,  1'b0,  8);   // GOT1 + x=0 -> detected=(GOT1==GOT10)&&0=0
        aplica_bit(1'b1,  1'b1,  9);   // GOT10+ x=1 -> detected=1 <- DETECCAO
        aplica_bit(1'b1,  1'b0, 10);   // GOT1 + x=1 -> detected=(GOT1==GOT10)&&1=0
        aplica_bit(1'b1,  1'b0, 11);   // GOT1 + x=1 -> detected=(GOT1==GOT10)&&1=0

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
