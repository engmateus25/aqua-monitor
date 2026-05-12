// =============================================================================
// sequence_detector_mealy.sv -- Detector de sequencia "101" (Mealy FSM)
// Unidade 5 | Capitulo 2 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Alexandre Almeida
// Data  : Maio 2026
// =============================================================================
// Arquitetura Mealy: saida depende do estado atual E da entrada atual.
// Vantagem: um estado a menos que Moore (3 vs 4 estados).
// Saida gerada no mesmo ciclo da transicao (resposta mais rapida).
// Deteccao com sobreposicao (overlapping).
// Reset assincrono ativo em nivel baixo (rst_n).
// Estilo tres processos: registrador de estado | logica de proximo estado/saida
// =============================================================================

module sequence_detector_mealy #(
    parameter int DATA_WIDTH = 1       // largura do bit de entrada (sempre 1 neste modulo)
)(
    input  logic clk,                  // clock (borda de subida)
    input  logic rst_n,                // reset assincrono ativo baixo
    input  logic x,                    // bit serial de entrada
    output logic sequence_detected     // '1' quando "101" completado neste ciclo
);

    // -------------------------------------------------------------------------
    // Definicao de estados (codificacao binaria)
    // -------------------------------------------------------------------------
    typedef enum logic [1:0] {
        IDLE  = 2'b00,   // estado inicial / sem historico util
        GOT1  = 2'b01,   // ultimo bit recebido foi '1'
        GOT10 = 2'b10    // ultimos dois bits foram "10"
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
    //   IDLE  + 0 -> IDLE  |  IDLE  + 1 -> GOT1
    //   GOT1  + 0 -> GOT10 |  GOT1  + 1 -> GOT1
    //   GOT10 + 0 -> IDLE  |  GOT10 + 1 -> GOT1   (sobreposicao: "1" inicia nova seq.)
    // =========================================================================
    always_comb begin
        unique case (state)
            IDLE:    if (x) next_state = GOT1;  else next_state = IDLE;
            GOT1:    if (x) next_state = GOT1;  else next_state = GOT10;
            GOT10:   if (x) next_state = GOT1;  else next_state = IDLE;  // sobreposicao
            default: next_state = IDLE;
        endcase
    end

    // =========================================================================
    // PROCESSO 3: Logica de saida Mealy (depende do estado E da entrada)
    // Saida = '1' apenas quando estado == GOT10 E entrada x == '1'
    // =========================================================================
    always_comb begin
        sequence_detected = (state == GOT10) && (x == 1'b1);
    end

endmodule
