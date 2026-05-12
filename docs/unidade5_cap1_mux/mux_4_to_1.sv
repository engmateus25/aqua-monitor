// =============================================================================
// mux_4_to_1.sv -- Multiplexador 4-para-1 parametrico em SystemVerilog
// Unidade 5 | Capitulo 1 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Alexandre Almeida
// Data  : Maio 2026
// =============================================================================

module mux_4_to_1 #(
    parameter int DATA_WIDTH = 8      // largura dos dados em bits (padrao: 8)
)(
    input  logic [DATA_WIDTH-1:0] d0, // entrada 0 (selecionada quando s = 2'b00)
    input  logic [DATA_WIDTH-1:0] d1, // entrada 1 (selecionada quando s = 2'b01)
    input  logic [DATA_WIDTH-1:0] d2, // entrada 2 (selecionada quando s = 2'b10)
    input  logic [DATA_WIDTH-1:0] d3, // entrada 3 (selecionada quando s = 2'b11)
    input  logic [1:0]            s,  // linhas de selecao (2 bits -> 4 estados)
    output logic [DATA_WIDTH-1:0] y   // saida unica
);

    // Logica combinacional pura: sempre_comb garante avaliacao imediata de
    // qualquer mudanca em d0..d3 ou s, sem necessidade de clock.
    always_comb begin
        unique case (s)
            2'b00:   y = d0;
            2'b01:   y = d1;
            2'b10:   y = d2;
            2'b11:   y = d3;
            default: y = '0;  // estado seguro para X/Z inesperado em s
        endcase
    end

endmodule
