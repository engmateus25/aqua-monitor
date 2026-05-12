// =============================================================================
// alu8.sv -- ALUChip v1.0: Unidade Logico-Aritmetica de 8 bits
// Unidade 7 | Capitulo 5 | PADIS
// Autor : Romulo da Silva Lira
// Prof. : Andre Feitosa
// =============================================================================
// Operacoes (op[2:0]):
//   000 ADD  -- A + B              (atualiza C, V)
//   001 SUB  -- A - B              (atualiza C, V)
//   010 AND  -- A & B
//   011 OR   -- A | B
//   100 XOR  -- A ^ B
//   101 NOT  -- ~A
//   110 SHL  -- A << 1, LSB=0, C=A[7]
//   111 SHR  -- A >> 1, MSB=0, C=A[0]
//
// Flags:
//   Z -- Zero      : result == 8'h00
//   C -- Carry     : carry-out / shift-out
//   V -- Overflow  : estouro de sinal (so ADD/SUB)
//   N -- Negativo  : result[7]
// =============================================================================

module alu8 (
    input  logic [7:0] a,          // operando A
    input  logic [7:0] b,          // operando B
    input  logic [2:0] op,         // codigo da operacao
    output logic [7:0] result,     // resultado de 8 bits
    output logic       flag_z,     // Zero
    output logic       flag_c,     // Carry / borrow / shift-out
    output logic       flag_v,     // Overflow (sinal)
    output logic       flag_n      // Negativo (MSB do resultado)
);

    logic [8:0] wide;   // 9 bits: [8]=carry, [7:0]=result

    // Bits extraidos para compatibilidade com Icarus (constant selects)
    logic       a_msb;   // a[7]
    logic       b_msb;   // b[7]
    logic       a_lsb;   // a[0]
    logic [6:0] a_lo7;   // a[6:0]
    logic [6:0] a_hi7;   // a[7:1]
    assign a_msb = a[7];
    assign b_msb = b[7];
    assign a_lsb = a[0];
    assign a_lo7 = a[6:0];
    assign a_hi7 = a[7:1];

    always_comb begin
        case (op)
            3'b000: wide = {1'b0, a} + {1'b0, b};          // ADD
            3'b001: wide = {1'b0, a} + {1'b0, ~b} + 9'd1;  // SUB
            3'b010: wide = {1'b0, a & b};                   // AND
            3'b011: wide = {1'b0, a | b};                   // OR
            3'b100: wide = {1'b0, a ^ b};                   // XOR
            3'b101: wide = {1'b0, ~a};                      // NOT
            3'b110: wide = {a_msb, a_lo7, 1'b0};            // SHL
            3'b111: wide = {a_lsb, 1'b0, a_hi7};            // SHR
            default: wide = 9'b0;
        endcase
    end

    // Overflow calculado fora do always_comb para evitar bit-selects internos
    logic res_msb;
    assign res_msb = wide[7];
    assign flag_v  = ((op == 3'b000) & ((~a_msb & ~b_msb &  res_msb) |
                                         ( a_msb &  b_msb & ~res_msb))) |
                     ((op == 3'b001) & ((~a_msb &  b_msb &  res_msb) |
                                         ( a_msb & ~b_msb & ~res_msb)));

    assign result = wide[7:0];
    assign flag_c = wide[8];
    assign flag_z = (wide[7:0] == 8'h00);
    assign flag_n = wide[7];

endmodule
