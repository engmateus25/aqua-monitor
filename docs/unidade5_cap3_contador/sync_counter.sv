// =============================================================================
// sync_counter.sv -- Contador Sincrono de 4 bits
// Unidade 5 | Capitulo 3 | Capacitacao Profissional em Microeletronica (PADIS)
// Autor : Matheus Serrao Uchoa   Matricula: 22052633
// Prof. : Thiago Brito
// Data  : Maio 2026
// =============================================================================
// Funcionalidades:
//   - Contagem crescente (up-counter): incrementa em 1 a cada borda de clock
//   - Reset assincrono ativo em nivel baixo (rst_n): zera imediatamente
//   - Enable sincrono ativo em nivel alto (en): incrementa somente se en=1
//   - Overflow: cicla de 15 (4'b1111) para 0 (4'b0000) automaticamente
// =============================================================================

module sync_counter (
    input  logic       clk,        // clock (borda de subida)
    input  logic       rst_n,      // reset assincrono ativo baixo
    input  logic       en,         // enable sincrono ativo alto
    output logic [3:0] count       // valor atual do contador (0..15)
);

    // Logica sequencial: reset assincrono + enable sincrono + overflow natural
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            count <= 4'b0000;      // reset assincrono: zera imediatamente
        else if (en)
            count <= count + 1'b1; // incremento sincrono (overflow automatico: 15->0)
        // se en=0: count mantem valor (sem else => sem latch em always_ff)
    end

endmodule
