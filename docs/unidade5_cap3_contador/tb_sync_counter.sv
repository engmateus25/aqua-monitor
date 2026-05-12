// =============================================================================
// tb_sync_counter.sv -- Testbench para sync_counter
// Unidade 5 | Capitulo 3 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Thiago Brito
// =============================================================================
`timescale 1ns/1ps

module tb_sync_counter;

    // -------------------------------------------------------------------------
    // Sinais
    // -------------------------------------------------------------------------
    logic       clk;
    logic       rst_n;
    logic       en;
    logic [3:0] count;

    int erros  = 0;
    int acertos = 0;

    // -------------------------------------------------------------------------
    // Instanciacao do DUT
    // -------------------------------------------------------------------------
    sync_counter dut (
        .clk   (clk),
        .rst_n (rst_n),
        .en    (en),
        .count (count)
    );

    // -------------------------------------------------------------------------
    // Clock: periodo 10 ns (50 MHz)
    // -------------------------------------------------------------------------
    initial clk = 0;
    always #5 clk = ~clk;

    // -------------------------------------------------------------------------
    // Monitor continuo: imprime toda mudanca relevante
    // -------------------------------------------------------------------------
    initial begin
        $monitor("t=%4t ns | clk=%b rst_n=%b en=%b | count=%02d (4'b%04b)",
                 $time, clk, rst_n, en, count, count);
    end

    // -------------------------------------------------------------------------
    // Tarefa: verifica valor esperado apos posedge
    // -------------------------------------------------------------------------
    task automatic verifica(
        input logic [3:0] esperado,
        input string      descricao
    );
        @(posedge clk); #1;
        if (count !== esperado) begin
            $display("  [FALHA] %s | count=%0d | Esperado=%0d", descricao, count, esperado);
            erros++;
        end else begin
            $display("  [OK]    %s | count=%0d", descricao, count);
            acertos++;
        end
    endtask

    // -------------------------------------------------------------------------
    // Tarefa: avanca N ciclos de clock sem verificacao
    // -------------------------------------------------------------------------
    task automatic aguarda(input int n);
        repeat(n) @(posedge clk);
        #1;
    endtask

    // -------------------------------------------------------------------------
    // Sequencia de testes
    // -------------------------------------------------------------------------
    initial begin
        $dumpfile("dump_counter.vcd");
        $dumpvars(0, tb_sync_counter);

        $display("========================================================");
        $display("  Simulacao: Contador Sincrono 4 bits");
        $display("  Sequencia: rst_n / enable / disable / overflow / reset");
        $display("========================================================\n");

        // ------------------------------------------------------------------
        // TESTE 1: Reset assincrono
        // ------------------------------------------------------------------
        $display("--- TESTE 1: Reset assincrono (rst_n = 0) ---");
        rst_n = 0; en = 0;
        #3; // reset assincrono: conta deve ser 0 imediatamente (sem esperar clock)
        if (count !== 4'b0000) begin
            $display("  [FALHA] Reset assincrono: count=%0d esperado=0", count); erros++;
        end else begin
            $display("  [OK]    Reset assincrono imediato: count=0"); acertos++;
        end
        @(posedge clk); #1;
        rst_n = 1;

        // ------------------------------------------------------------------
        // TESTE 2: Enable sincrono -- conta de 0 a 7
        // ------------------------------------------------------------------
        $display("\n--- TESTE 2: Enable sincrono (en=1), conta 0->7 ---");
        en = 1;
        verifica(4'd1,  "en=1, ciclo  1");
        verifica(4'd2,  "en=1, ciclo  2");
        verifica(4'd3,  "en=1, ciclo  3");
        verifica(4'd4,  "en=1, ciclo  4");
        verifica(4'd5,  "en=1, ciclo  5");
        verifica(4'd6,  "en=1, ciclo  6");
        verifica(4'd7,  "en=1, ciclo  7");

        // ------------------------------------------------------------------
        // TESTE 3: Desabilitar contador (en=0), count deve manter valor
        // ------------------------------------------------------------------
        $display("\n--- TESTE 3: Enable desativado (en=0), count congela em 7 ---");
        en = 0;
        verifica(4'd7,  "en=0, ciclo  1 (congela)");
        verifica(4'd7,  "en=0, ciclo  2 (congela)");
        verifica(4'd7,  "en=0, ciclo  3 (congela)");

        // ------------------------------------------------------------------
        // TESTE 4: Reativar enable -- continua de 7
        // ------------------------------------------------------------------
        $display("\n--- TESTE 4: Reativa en=1, continua de 7 ---");
        en = 1;
        verifica(4'd8,  "en=1 reativado, count=8");
        verifica(4'd9,  "en=1, count=9");
        verifica(4'd10, "en=1, count=10");

        // ------------------------------------------------------------------
        // TESTE 5: Toggle enable durante contagem
        // ------------------------------------------------------------------
        $display("\n--- TESTE 5: Toggle en durante contagem ---");
        en = 0; verifica(4'd10, "en=0, count congela 10");
        en = 1; verifica(4'd11, "en=1, count=11");
        en = 0; verifica(4'd11, "en=0, count congela 11");
        en = 1; verifica(4'd12, "en=1, count=12");

        // ------------------------------------------------------------------
        // TESTE 6: Contagem ate overflow (12 -> 15 -> 0)
        // ------------------------------------------------------------------
        $display("\n--- TESTE 6: Overflow (15 -> 0) ---");
        verifica(4'd13, "count=13");
        verifica(4'd14, "count=14");
        verifica(4'd15, "count=15 (maximo)");
        verifica(4'd0,  "overflow: count=0");
        verifica(4'd1,  "pos-overflow: count=1");

        // ------------------------------------------------------------------
        // TESTE 7: Reset assincrono durante contagem ativa
        // ------------------------------------------------------------------
        $display("\n--- TESTE 7: Reset assincrono durante contagem ativa ---");
        en = 1;
        aguarda(3);
        // Aplica reset no meio do ciclo (nao na borda)
        #3; rst_n = 0;
        #1;
        if (count !== 4'b0000) begin
            $display("  [FALHA] Reset assincrono mid-cycle: count=%0d esperado=0", count); erros++;
        end else begin
            $display("  [OK]    Reset assincrono mid-cycle: count=0 imediato"); acertos++;
        end
        @(posedge clk); #1;
        rst_n = 1;
        verifica(4'd1, "apos reset, continua contagem: count=1");
        verifica(4'd2, "count=2");

        // ------------------------------------------------------------------
        // RESULTADO FINAL
        // ------------------------------------------------------------------
        $display("\n========================================================");
        $display("  Acertos: %0d | Erros: %0d", acertos, erros);
        if (erros == 0)
            $display("  >>> RESULTADO: APROVADO <<<");
        else
            $display("  >>> RESULTADO: REPROVADO -- %0d erro(s) <<<", erros);
        $display("  Simulacao concluida em %0t", $time);
        $display("========================================================");
        $finish;
    end

endmodule
