// =============================================================================
// alu8_chip_top.sv -- Top-level: ALUChip v1.0
// Unidade Logico-Aritmetica de 8 bits
// Unidade 7 | Capitulo 5 | PADIS
// Autor : Romulo da Silva Lira
// Prof. : Andre Feitosa
// =============================================================================
// Hierarquia:
//   alu8_chip_top
//   └── alu8  -- ULA combinacional 8 bits / 8 operacoes / 4 flags
//
// Especificacoes:
//   Processo : CMOS 0.35um | VDD = 3.3V
//   Funcao   : ULA 8 bits -- ADD, SUB, AND, OR, XOR, NOT, SHL, SHR
//   Latencia : 0 ciclos (logica puramente combinacional)
//   Aplicacao: Nucleo aritmetico de microprocessadores, DSP, controladores
// =============================================================================

module alu8_chip_top (
    input  logic [7:0] a,        // operando A
    input  logic [7:0] b,        // operando B
    input  logic [2:0] op,       // selecao de operacao (000..111)
    output logic [7:0] result,   // resultado de 8 bits
    output logic       flag_z,   // Zero
    output logic       flag_c,   // Carry / Borrow / Shift-out
    output logic       flag_v,   // Overflow (sinal)
    output logic       flag_n    // Negativo
);

    alu8 u_alu (
        .a       (a),
        .b       (b),
        .op      (op),
        .result  (result),
        .flag_z  (flag_z),
        .flag_c  (flag_c),
        .flag_v  (flag_v),
        .flag_n  (flag_n)
    );

endmodule
