// =============================================================================
// hamming_decoder.sv -- Decodificador/Corretor Hamming(7,4)
// HammingChip v1.0 | Unidade 7 | Capitulo 5 | PADIS
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Thiago Brito
// =============================================================================
// Recebe codeword de 7 bits (possivelmente com 1 erro de bit).
// Calcula a sindrome (3 bits) para localizar e corrigir o erro.
// Sindrome = {s4, s2, s1}:
//   s1 = c[0]^c[2]^c[4]^c[6]
//   s2 = c[1]^c[2]^c[5]^c[6]
//   s4 = c[3]^c[4]^c[5]^c[6]
// Valor da sindrome indica a posicao do bit errado (1-7), 0 = sem erro.
// Apos correcao, extrai os 4 bits de dados: {c[6],c[5],c[4],c[2]}.
// =============================================================================

module hamming_decoder (
    input  logic [6:0] code_in,    // codeword recebido (pode conter 1 erro)
    output logic [3:0] data_out,   // dados corrigidos
    output logic [2:0] syndrome,   // {s4,s2,s1}: posicao do erro (0=sem erro)
    output logic       error_flag  // 1 se erro detectado e corrigido
);

    logic [6:0] corrected;

    // Calculo da sindrome
    logic s1, s2, s4;
    assign s1 = code_in[0] ^ code_in[2] ^ code_in[4] ^ code_in[6];
    assign s2 = code_in[1] ^ code_in[2] ^ code_in[5] ^ code_in[6];
    assign s4 = code_in[3] ^ code_in[4] ^ code_in[5] ^ code_in[6];

    assign syndrome   = {s4, s2, s1};
    assign error_flag = (syndrome != 3'b000);

    // Correcao: inverte o bit na posicao indicada pela sindrome (1-indexed)
    always_comb begin
        corrected = code_in;
        if (error_flag) begin
            // syndrome contem a posicao (1 a 7) do bit errado
            // indice do array = posicao - 1
            case (syndrome)
                3'd1: corrected[0] = ~code_in[0];
                3'd2: corrected[1] = ~code_in[1];
                3'd3: corrected[2] = ~code_in[2];
                3'd4: corrected[3] = ~code_in[3];
                3'd5: corrected[4] = ~code_in[4];
                3'd6: corrected[5] = ~code_in[5];
                3'd7: corrected[6] = ~code_in[6];
                default: corrected = code_in;
            endcase
        end
    end

    // Extrai bits de dados do codeword corrigido: posicoes 3,5,6,7 (1-indexed)
    // = indices 2,4,5,6 (0-indexed) = {d4=c[6], d3=c[5], d2=c[4], d1=c[2]}
    assign data_out = {corrected[6], corrected[5], corrected[4], corrected[2]};

endmodule
