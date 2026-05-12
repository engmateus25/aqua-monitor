// =============================================================================
// sequence_detector_moore.sv -- Detector de sequencia "101" (Moore FSM)
// Unidade 5 | Capitulo 2 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Alexandre Almeida
// Data  : Maio 2026
// =============================================================================
// Arquitetura Moore: saida depende SOMENTE do estado atual.
// Deteccao com sobreposicao (overlapping): apos "101", o ultimo "1" reaproveitado.
// Reset assincrono ativo em nivel baixo (rst_n).
// Estilo tres processos: registrador de estado | logica de proximo estado | logica de saida
// =============================================================================

module sequence_detector_moore #(
    parameter int DATA_WIDTH = 1       // largura do bit de entrada (sempre 1 neste modulo)
)(
    input  logic clk,                  // clock (borda de subida)
    input  logic rst_n,                // reset assincrono ativo baixo
    input  logic x,                    // bit serial de entrada
    output logic sequence_detected     // '1' quando "101" for detectado (ciclo completo)
);

    // -------------------------------------------------------------------------
    // Definicao de estados (codificacao binaria sequencial)
    // -------------------------------------------------------------------------
    typedef enum logic [1:0] {
        IDLE   = 2'b00,   // estado inicial / sem historico util
        GOT1   = 2'b01,   // ultimo bit recebido foi '1'
        GOT10  = 2'b10,   // ultimos dois bits foram "10"
        GOT101 = 2'b11    // ultimos tres bits foram "101" -> deteccao!
    } state_t;

    state_t state, next_state;

    // =========================================================================
    // PROCESSO 1: Registrador de estado (sequencial, reset assincrono)
    // =========================================================================
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    // =========================================================================
    // PROCESSO 2: Logica de proximo estado (combinacional)
    // Tabela de transicoes:
    //   IDLE   + 0 -> IDLE    |  IDLE   + 1 -> GOT1
    //   GOT1   + 0 -> GOT10   |  GOT1   + 1 -> GOT1
    //   GOT10  + 0 -> IDLE    |  GOT10  + 1 -> GOT101
    //   GOT101 + 0 -> GOT10   |  GOT101 + 1 -> GOT1   (sobreposicao)
    // =========================================================================
    always_comb begin
        unique case (state)
            IDLE:    if (x) next_state = GOT1;   else next_state = IDLE;
            GOT1:    if (x) next_state = GOT1;   else next_state = GOT10;
            GOT10:   if (x) next_state = GOT101; else next_state = IDLE;
            GOT101:  if (x) next_state = GOT1;   else next_state = GOT10;  // sobreposicao
            default: next_state = IDLE;
        endcase
    end

    // =========================================================================
    // PROCESSO 3: Logica de saida Moore (depende APENAS do estado atual)
    // =========================================================================
    always_comb begin
        sequence_detected = (state == GOT101);
    end

endmodule
