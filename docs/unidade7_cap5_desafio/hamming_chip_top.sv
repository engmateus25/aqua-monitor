// =============================================================================
// hamming_chip_top.sv -- Top-level: HammingChip v1.0
// Codec Hamming(7,4) com Correcao de Erros de 1 bit
// Unidade 7 | Capitulo 5 | PADIS
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Thiago Brito
// =============================================================================
// Hierarquia:
//   hamming_chip_top
//   ├── hamming_encoder  -- codifica 4->7 bits (combinacional)
//   └── hamming_decoder  -- decodifica/corrige 7->4 bits (combinacional)
//
// Especificacoes:
//   Processo : CMOS 0.35um | VDD = 3.3V
//   Funcao   : Codec ECC Hamming(7,4) -- detecta e corrige 1 erro de bit
//   Latencia : 0 ciclos (logica puramente combinacional)
//   Aplicacao: Memoria ECC, comunicacao espacial, barramento seguro
// =============================================================================

module hamming_chip_top (
    input  logic [3:0] data_in,      // dados a codificar
    output logic [6:0] encoded,      // codeword codificado (7 bits)

    input  logic [6:0] received,     // codeword recebido (canal ruidoso)
    output logic [3:0] data_out,     // dados recuperados (corrigidos)
    output logic [2:0] syndrome,     // {s4,s2,s1}: sindrome do erro
    output logic       error_flag    // 1 se erro foi detectado/corrigido
);

    hamming_encoder u_enc (
        .data_in  (data_in),
        .code_out (encoded)
    );

    hamming_decoder u_dec (
        .code_in    (received),
        .data_out   (data_out),
        .syndrome   (syndrome),
        .error_flag (error_flag)
    );

endmodule
