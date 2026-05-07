`timescale 1ns / 1ps

module tb_sar_fsm;

    // Entradas
    reg clk;
    reg rst_n;
    reg start;
    reg comp_out;

    // Saídas
    wire [3:0] dac_in;
    wire eoc;
    wire [3:0] data_out;
    wire sample;

    // Instancia o Módulo
    sar_fsm_4bit uut (
        .clk(clk), 
        .rst_n(rst_n), 
        .start(start), 
        .comp_out(comp_out), 
        .dac_in(dac_in), 
        .eoc(eoc), 
        .data_out(data_out),
        .sample(sample)
    );

    // Geração do Clock (período de 10ns = 100MHz)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Estímulos
    initial begin
        // Condição Inicial
        rst_n = 0;
        start = 0;
        comp_out = 0;
        
        // Aguarda 20ns e solta o reset
        #20;
        rst_n = 1;
        
        // Dá o pulso de START
        #10;
        start = 1;
        #10;
        start = 0;
        
        // Simulação da lógica do comparador.
        // Vamos supor que a tensão analógica Vin seja tal que o resultado digital esperado é 1010 (Decimal 10).
        // Assim, as respostas do comparador serão: 
        // BIT3 (Peso 8): comp_out = 1 (Vin > 8)
        // BIT2 (Peso 4): comp_out = 0 (Vin < 8+4=12)
        // BIT1 (Peso 2): comp_out = 1 (Vin > 8+0+2=10)
        // BIT0 (Peso 1): comp_out = 0 (Vin < 8+0+2+1=11)
        
        // Aguarda o estado SAMPLE terminar (estado 1)
        #10; // Agora está no estado BIT3 (estado 2)
        
        // Testando BIT 3
        comp_out = 1; // 1
        #10; // Pula para BIT2
        
        // Testando BIT 2
        comp_out = 0; // 0
        #10; // Pula para BIT1
        
        // Testando BIT 1
        comp_out = 1; // 1
        #10; // Pula para BIT0
        
        // Testando BIT 0
        comp_out = 0; // 0
        #10; // Pula para DONE
        
        // Aguarda o EOC e checa o resultado
        #10;
        if (eoc && data_out == 4'b1010) begin
            $display("SUCESSO: A conversão terminou corretamente. Resultado = %b", data_out);
        end else begin
            $display("FALHA: Resultado inesperado ou conversão não terminou. Resultado = %b", data_out);
        end
        
        #20;
        $finish;
    end
    
    // Monitor de variáveis
    initial begin
        $monitor("Time: %0dns | State: %0d | start: %b | comp_out: %b | dac_in: %b | data_out: %b | eoc: %b", 
                 $time, uut.state, start, comp_out, dac_in, data_out, eoc);
    end

endmodule
