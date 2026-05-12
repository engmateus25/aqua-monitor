// =============================================================================
// hamming_encoder.sv -- Codificador Hamming(7,4)
// HammingChip v1.0 | Unidade 7 | Capitulo 5 | PADIS
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Thiago Brito
// =============================================================================
// Codifica 4 bits de dados em 7 bits (3 bits de paridade adicionados).
// Estrutura do codeword (indice 0 = LSB):
//   [6]  [5]  [4]  [3]  [2]  [1]  [0]
//    d4   d3   d2   p4   d1   p2   p1
//
// Calculos de paridade:
//   p1 (pos 1) = d1 ^ d2 ^ d4     (cobre posicoes 1,3,5,7)
//   p2 (pos 2) = d1 ^ d3 ^ d4     (cobre posicoes 2,3,6,7)
//   p4 (pos 4) = d2 ^ d3 ^ d4     (cobre posicoes 4,5,6,7)
// =============================================================================

module hamming_encoder (
    input  logic [3:0] data_in,    // [3]=d4  [2]=d3  [1]=d2  [0]=d1
    output logic [6:0] code_out    // [6]=d4 [5]=d3 [4]=d2 [3]=p4 [2]=d1 [1]=p2 [0]=p1
);

    logic d1, d2, d3, d4;
    logic p1, p2, p4;

    assign {d4, d3, d2, d1} = data_in;

    assign p1 = d1 ^ d2 ^ d4;   // paridade impar sobre posicoes 1,3,5,7
    assign p2 = d1 ^ d3 ^ d4;   // paridade impar sobre posicoes 2,3,6,7
    assign p4 = d2 ^ d3 ^ d4;   // paridade impar sobre posicoes 4,5,6,7

    assign code_out = {d4, d3, d2, p4, d1, p2, p1};

endmodule
