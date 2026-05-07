`timescale 1ns / 1ps

module sar_fsm_4bit (
    input wire clk,          // Clock do sistema
    input wire rst_n,        // Reset assíncrono ativo em baixo
    input wire start,        // Pulso de início de conversão
    input wire comp_out,     // Saída do comparador analógico (1 = Vin > Vdac, 0 = Vin < Vdac)
    
    output reg [3:0] dac_in, // Controle das chaves do DAC de capacitores
    output reg eoc,          // End Of Conversion (1 = Conversão finalizada)
    output reg [3:0] data_out, // Resultado digital final
    output reg sample        // Sinal de controle da chave de amostragem (S&H)
);

    // Estados da FSM (One-Hot ou Binário)
    localparam IDLE    = 3'd0;
    localparam SAMPLE  = 3'd1;
    localparam BIT3    = 3'd2; // Testa MSB (Bit 3)
    localparam BIT2    = 3'd3;
    localparam BIT1    = 3'd4;
    localparam BIT0    = 3'd5; // Testa LSB (Bit 0)
    localparam DONE    = 3'd6;

    reg [2:0] state, next_state;

    // Lógica de transição de estado (Sequencial)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end

    // Lógica do Próximo Estado (Combinacional)
    always @(*) begin
        case (state)
            IDLE:   if (start) next_state = SAMPLE; else next_state = IDLE;
            SAMPLE: next_state = BIT3;
            BIT3:   next_state = BIT2;
            BIT2:   next_state = BIT1;
            BIT1:   next_state = BIT0;
            BIT0:   next_state = DONE;
            DONE:   next_state = IDLE;
            default: next_state = IDLE;
        endcase
    end

    // Lógica de Saída e Controle do DAC (Sequencial)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dac_in   <= 4'b0000;
            data_out <= 4'b0000;
            eoc      <= 1'b0;
            sample   <= 1'b0;
        end else begin
            // Valores padrão para os sinais de pulso
            eoc    <= 1'b0;
            sample <= 1'b0;

            case (state)
                IDLE: begin
                    if (start) begin
                        sample <= 1'b1; // Inicia a amostragem
                        dac_in <= 4'b0000;
                    end
                end

                SAMPLE: begin
                    // Termina a amostragem e prepara para testar o MSB
                    dac_in <= 4'b1000; // Coloca VREF/2 (Bit 3 em ALTO)
                end

                BIT3: begin
                    // Avalia o comparador para o MSB
                    if (comp_out) begin
                        dac_in[3] <= 1'b1; // Mantém MSB se Vin > Vdac
                    end else begin
                        dac_in[3] <= 1'b0; // Derruba MSB se Vin < Vdac
                    end
                    // Seta o próximo bit a ser testado
                    dac_in[2] <= 1'b1;
                end

                BIT2: begin
                    // Avalia Bit 2
                    if (comp_out) dac_in[2] <= 1'b1;
                    else          dac_in[2] <= 1'b0;
                    
                    dac_in[1] <= 1'b1; // Testa o próximo
                end

                BIT1: begin
                    // Avalia Bit 1
                    if (comp_out) dac_in[1] <= 1'b1;
                    else          dac_in[1] <= 1'b0;
                    
                    dac_in[0] <= 1'b1; // Testa o LSB
                end

                BIT0: begin
                    // Avalia LSB
                    if (comp_out) dac_in[0] <= 1'b1;
                    else          dac_in[0] <= 1'b0;
                end

                DONE: begin
                    // Fim da conversão, salva o resultado
                    eoc <= 1'b1;
                    data_out <= dac_in;
                    dac_in <= 4'b0000; // Reseta o DAC para poupar energia (opcional)
                end
            endcase
        end
    end

endmodule
