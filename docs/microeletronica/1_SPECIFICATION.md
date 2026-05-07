# Etapa 1: Descrição do Circuito (Especificação do SAR ADC)

**Projeto:** Conversor Analógico-Digital de Aproximações Sucessivas (SAR ADC) de 4-Bits.
**Aplicação:** Digitalização dos Sensores de Turbidez/TDS do *Aqua Monitor*.

## 1. Justificativa
O microcontrolador do *Aqua Monitor* precisa ler os sensores analógicos. Embora microcontroladores como o ESP32 tenham ADCs internos, projetar um ADC dedicado do zero é o ápice do design de circuitos integrados. O **SAR ADC** foi escolhido por ser a arquitetura mais utilizada na indústria para amostragem de dados devido ao seu baixo consumo de energia (excelente para IoT) e excelente compromisso entre velocidade e área de silício.

## 2. Arquitetura do Sistema
O chip operará no modo de Sinais Mistos e será dividido nos seguintes blocos:

1. **Matriz de Capacitores (Charge-Redistribution DAC):**
   * Em vez de usar resistores (que consomem área massiva e energia estática), usaremos capacitores integrados.
   * A matriz ponderada binária fará simultaneamente o *Sample & Hold* do sinal do sensor e a geração de tensão para comparação.
   * **Pesos (4-bits):** 8C, 4C, 2C, 1C e um capacitor de terminação de 1C (Total: 16 capacitores unitários).

2. **Comparador de Tensão (Analógico):**
   * Bloco puramente analógico. Pode ser um simples Op-Amp de 2 estágios em malha aberta ou um comparador dinâmico (*Latch*).
   * Função: Dizer se a tensão do DAC ($V_{DAC}$) é maior ou menor que o terminal de aterramento/referência durante a fase de conversão.

3. **Lógica de Aproximações Sucessivas (SAR FSM - Digital):**
   * Um circuito digital sequencial que, a cada pulso de clock, decide o valor do próximo bit com base na resposta do comparador (Busca Binária).

## 3. Especificações Técnicas (Metas do Projeto)

Considerando uma tecnologia educacional padrão (ex: **CMOS 180nm ou 130nm**):

| Parâmetro | Símbolo | Valor Alvo (Target) |
| :--- | :--- | :--- |
| Tecnologia | L min | $0.18 \, \mu m$ (180nm) |
| Tensão de Alimentação | $V_{DD}$ / $V_{REF}$ | $1.8 \text{ V}$ |
| Resolução | $N$ | 4 Bits (16 níveis de tensão) |
| Frequência de Amostragem | $f_S$ | $\approx 100 \text{ kS/s}$ (Suficiente para sensores lentos da água) |
| LSB (Tensão do bit menos significativo) | $V_{LSB}$ | $\frac{V_{DD}}{2^4} = 112.5 \text{ mV}$ |
| Frequência de Clock do SAR | $f_{CLK}$ | $\ge 6 \times f_S$ (1 ciclo p/ amostrar + 4 para converter + 1 reset) |
| Capacitor Unitário | $C_0$ | $\approx 50 \text{ fF}$ a $100 \text{ fF}$ (Para casar kTC noise) |
| Potência Total | $P_{diss}$ | $\le 100 \, \mu\text{W}$ |

## 4. O Fluxo de Operação do SAR
1. **Fase de Amostragem (Sample):** A chave de topo liga todas as placas superiores ao terra, e as placas inferiores são conectadas à tensão analógica do Sensor ($V_{IN}$).
2. **Fase de Hold:** A chave de topo abre. As placas inferiores são aterradas. A tensão no nodo superior (ligado ao comparador) vai para $-V_{IN}$.
3. **Fase de Redistribuição (Bit a bit):**
   * O MSB (capacitor 8C) é ligado ao $V_{REF}$. A tensão no comparador sobre para $-V_{IN} + \frac{V_{REF}}{2}$.
   * O comparador avalia. Se o resultado for $> 0$, o MSB é 0 e o capacitor volta ao terra. Se $< 0$, o MSB é 1 e o capacitor continua no $V_{REF}$.
   * O processo repete até o LSB.

## 5. Próximo Passo
Desenvolver e validar a FSM do SAR em código (Verilog) e equacionar os transistores do Comparador.
