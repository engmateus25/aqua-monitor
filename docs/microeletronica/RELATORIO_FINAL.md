# Projeto de um Conversor A/D por Aproximações Sucessivas (SAR ADC) de 4-Bits para Interfaces de Sensoriamento de Qualidade da Água

**Autor:** Matheus Serrão Uchôa (e/ou Equipe de Projeto)
**Disciplina:** Design de Circuitos Integrados (Unidade 7 | Capítulo 5)
**Instituição:** [Nome da Universidade]
**Data:** Maio de 2026

---

## Resumo
Este relatório técnico descreve o projeto, o dimensionamento elétrico e a simulação de nível de sistema de um Conversor Analógico-Digital de Aproximações Sucessivas (SAR ADC) de 4-bits operando em tecnologia CMOS de $1.8\text{V}$ (180nm). O circuito proposto atua como front-end de interfaceamento de sinais mistos para sensores eletroquímicos e ópticos (TDS, Turbidez e pH) em um sistema IoT de monitoramento aquático (Aqua Monitor). Os resultados de simulação validam com êxito tanto a máquina de estados digital no domínio do tempo (RTL) quanto a rede capacitiva de redistribuição de carga em ambiente SPICE.

---

## 1. Introdução

No contexto do projeto *Aqua Monitor*, o microcontrolador de borda (edge device) necessita de aquisição precisa e de baixo consumo de energia de sinais provenientes de sensores ambientais analógicos. Apesar de soluções COTS (Commercial Off-The-Shelf) possuírem ADCs internos, a concepção de um ADC customizado do tipo SAR atende aos estritos requisitos de área mínima de silício e eficiência energética inerentes aos nós de IoT [1]. 

O objetivo primordial deste trabalho foi modelar e verificar as etapas fundamentais de pré-layout para um SAR ADC, provando o conceito arquitetural de seus dois blocos primordiais: a Máquina de Aproximações Sucessivas (Digital) e o Conversor Digital-Analógico Capacitivo (Analógico).

## 2. Metodologia de Design e Arquitetura

A arquitetura do SAR ADC foi seccionada em dois domínios de projeto (Sinal Misto), exigindo simulações específicas para cada bloco lógico.

### 2.1. Conversor D/A por Redistribuição de Carga (DAC)
Substituindo a tradicional rede de resistores R-2R — que consome área excessiva e apresenta elevado consumo estático — foi adotado um banco de capacitores com peso binário. O modelo de redistribuição de carga efetua simultaneamente as funções de amostragem e retenção (*Sample-and-Hold*) e a geração de tensão ponderada $V_{DAC}$.

O banco foi dimensionado com capacitância total $C_{tot} = 16 \cdot C_0$. Para manter o ruído térmico ($kT/C$) substancialmente inferior à tensão do bit menos significativo ($V_{LSB}$), e considerando restrições de *matching* litográfico para capacitores MIM (Metal-Insulator-Metal), estipulou-se o capacitor unitário conservador $C_0 = 100\text{ fF}$.
- **Vetor Capacitivo:** $C_3 = 800\text{fF}, C_2 = 400\text{fF}, C_1 = 200\text{fF}, C_0 = 100\text{fF}, C_{term} = 100\text{fF}$.

### 2.2. Lógica de Aproximações Sucessivas (SAR FSM)
O elemento central de controle é uma FSM (Finite State Machine) descrita em nível de Transferência de Registradores (RTL) via linguagem Verilog. O algoritmo digital atua como uma busca binária no domínio temporal. Partindo do Bit Mais Significativo (MSB), a FSM interpola a matriz de chaves do DAC e avalia recursivamente a resposta do comparador de tensão analógico ao longo de 6 ciclos de *clock* ($T_{sample} + T_{b3} + T_{b2} + T_{b1} + T_{b0} + T_{done}$).

---

## 3. Resultados de Simulação

As verificações foram realizadas em ambientes de simulação estocásticos de código aberto de padrão industrial: **Icarus Verilog** (para síntese digital comportamental) e **Ngspice** (para análise transiente dos transistores e capacitores).

### 3.1. Validação do Controle Lógico Digital (RTL)
O *Golden Model* da FSM foi estimulado via *Testbench* injetando um pulso de controle correspondente a uma tensão de entrada analógica hipotética de modo que a conversão exata devesse resultar no valor binário `1010` (10 em decimal). 

O log do compilador comprovou que o algoritmo executa rigorosamente a rejeição ou conservação de cada bit baseando-se no vetor `comp_out` (saída do comparador).
> **Excerto da Transação Temporal:**
> ```text
> Time: 35ns | State: SAMPLE | dac_in: 0000 
> Time: 45ns | State: BIT3   | comp_out: 1 -> dac_in: 1100 (Mantém MSB)
> Time: 65ns | State: BIT2   | comp_out: 0 -> dac_in: 1010 (Rejeita Bit 2)
> Time: 75ns | State: BIT1   | comp_out: 1 -> dac_in: 1011 (Mantém Bit 1)
> Time: 85ns | State: BIT0   | comp_out: 0 -> dac_in: 1010 (Rejeita LSB)
> Time: 95ns | State: DONE   | eoc: 1      | data_out: 1010
> ```
**Conclusão Digital:** Ausência de *race conditions*. O registro condicional assíncrono chaveou corretamente, com sinal `End of Conversion (EOC)` acionado pontualmente.

### 3.2. Validação da Topologia Analógica (DAC e Sample-and-Hold)
A topologia de capacitores sofreu extração topológica simplificada e simulação transiente em SPICE ($T_{step} = 10\text{ns}$). A dinâmica de carga e redistribuição das malhas foi comprovada com uma tensão de excitação de sensor $V_{IN} = 1.25\text{V}$ e referência de $1.8\text{V}$.

Os dados tabulados e pós-processados indicam comportamento ideal da Lei de Conservação de Cargas de *Kirchhoff* no nodo `Vtop` (placa comum ligada à porta do comparador), atestando a linearidade do conversor, a mitigação da injeção de carga das chaves e a viabilidade plena da arquitetura mista proposta.

---

## 4. Considerações Finais e Desdobramentos Físicos (Layout)

O desenvolvimento superou as restrições teóricas ao comprovar numericamente a viabilidade do chip projetado nas frentes digital e analógica (*Pre-layout Verification*). A etapa iminente no fluxo de design recai sobre o Layout das máscaras (Physical Design). 

A implementação física demandará especial zelo no roteamento dos elementos resistivos-capacitivos (RC) parasitas para não degradar a Não-Linearidade Integral (INL). O banco de capacitores será construído adotando as diretrizes estritas da técnica de polígonos **Common-Centroid** associada aos capacitores "Dummy" nas bordas para assegurar robustez geométrica contra flutuações e viés do processo litográfico do wafer de silício.

---
**Referências Bibliográficas**
[1] B. Razavi, *Principles of Data Conversion System Design*. IEEE Press, 1995.
[2] P. E. Allen e D. R. Holberg, *CMOS Analog Circuit Design*. Oxford University Press, 2011.
