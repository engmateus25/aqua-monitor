// =============================================================================
// tb_mux_4_to_1.sv -- Testbench para mux_4_to_1
// Unidade 5 | Capitulo 1 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// =============================================================================
`timescale 1ns/1ps

module tb_mux_4_to_1;

    // -------------------------------------------------------------------------
    // Parametros e sinais
    // -------------------------------------------------------------------------
    parameter int DATA_WIDTH = 8;

    logic [DATA_WIDTH-1:0] d0, d1, d2, d3;
    logic [1:0]            s;
    logic [DATA_WIDTH-1:0] y;

    // Contador de erros para relatorio automatico PASS/FAIL
    int erros = 0;

    // -------------------------------------------------------------------------
    // Instanciacao do DUT (Design Under Test)
    // -------------------------------------------------------------------------
    mux_4_to_1 #(
        .DATA_WIDTH(DATA_WIDTH)
    ) dut (
        .d0(d0), .d1(d1), .d2(d2), .d3(d3),
        .s(s),
        .y(y)
    );

    // -------------------------------------------------------------------------
    // Tarefa auxiliar: aplica selecao, aguarda propagacao e verifica saida
    // -------------------------------------------------------------------------
    task automatic testa_mux(
        input logic [1:0]            sel,
        input logic [DATA_WIDTH-1:0] esperado
    );
        s = sel;
        #10;
        if (y !== esperado) begin
            $display("  [FALHA] t=%0t | S=%02b | Y=0x%02h | Esperado=0x%02h",
                     $time, s, y, esperado);
            erros++;
        end else begin
            $display("  [OK]    t=%0t | S=%02b | Y=0x%02h -> Esperado: 0x%02h",
                     $time, s, y, esperado);
        end
    endtask

    // -------------------------------------------------------------------------
    // Estimulos e verificacao
    // -------------------------------------------------------------------------
    initial begin
        // Exporta formas de onda para EPWave / GTKWave
        $dumpfile("dump.vcd");
        $dumpvars(0, tb_mux_4_to_1);

        // Valores de entrada fixos (hexadecimal)
        d0 = 8'hAA;
        d1 = 8'hBB;
        d2 = 8'hCC;
        d3 = 8'hDD;

        $display("=== Iniciando Simulacao do MUX 4:1 ===");
        $display("Valores de Entrada: D0=0x%02h | D1=0x%02h | D2=0x%02h | D3=0x%02h\n",
                  d0, d1, d2, d3);
        $display("%-8s  %-6s  %-10s  %-10s  %-6s",
                  "Tempo", "S", "Y (saida)", "Esperado", "Status");
        $display("%s", {"─", {60{"─"}}});

        // Testa todas as 4 combinacoes de selecao
        testa_mux(2'b00, d0);
        testa_mux(2'b01, d1);
        testa_mux(2'b10, d2);
        testa_mux(2'b11, d3);

        $display("\n%s", {"─", {60{"─"}}});
        if (erros == 0)
            $display(">>> RESULTADO: APROVADO -- 4/4 combinacoes corretas <<<");
        else
            $display(">>> RESULTADO: REPROVADO -- %0d erro(s) detectado(s) <<<", erros);

        $display("=== Simulacao Concluida em %0t ===", $time);
        $finish;
    end

endmodule
