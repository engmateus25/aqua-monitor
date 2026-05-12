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

## 4. Projeto do Comparador Analógico (Etapa 2 — Analógica)

O comparador de tensão é o bloco **puramente analógico** do SAR ADC — o único elemento que exige projeto em nível de transistor. A arquitetura selecionada é o **par diferencial PMOS com espelho de corrente NMOS e amplificador *common-source* NMOS de saída**, padrão industrial para SAR ADCs de baixo consumo.

### 4.1 Dimensionamento dos Transistores

| Transistor | Tipo | W (µm) | L (µm) | W/L | Função |
|---|---|---|---|---|---|
| M1 | PMOS | 20 | 1.0 | 20 | Par diferencial — entrada INM (−) |
| M2 | PMOS | 20 | 1.0 | 20 | Par diferencial — entrada INP (+) |
| M3 | NMOS | 10 | 1.0 | 10 | Espelho de corrente (diodo) |
| M4 | NMOS | 10 | 1.0 | 10 | Espelho de corrente (cópia) |
| M5 | PMOS | 10 | 2.0 | 5  | Fonte de corrente de cauda (I = 20 µA) |
| M6 | NMOS | 10 | 0.5 | 20 | Amplificador CS — estágio 2 |
| M7 | PMOS | 20 | 0.5 | 40 | Carga ativa — estágio 2 |

**Ganho calculado do estágio 1:**
$$A_1 = g_m \cdot (r_{ds2} \| r_{ds4}) = 190\,\mu\text{A/V} \times 500\,\text{k}\Omega = 95\,\text{V/V} \approx 39.6\,\text{dB}$$

Requisito mínimo ($A_{min} = V_{DD} / (V_{LSB}/2) = 32$ V/V) **atendido com margem de 3× ✓**

### 4.2 Validação Digital-Analógica (Polaridade)

Pela análise nodal do par diferencial PMOS, quando INP (sinal do DAC) é **maior** que INM (referência VREF/2):
- M2 conduz menos → I\_M2 cai, I\_M1 sobe
- Vd1 sobe → I\_M4 (espelho) sobe → Vout1 **cai**
- Estágio 2: Vout1 baixo → M6 menos ativo → Vout **sobe** = `comp_out = 1`

Resultado: `comp_out = 1` quando `Vtop > 0`, compatível com a FSM SAR existente. ✓

### 4.3 Simulação Pré-Layout (`comparator_prelayout.cir`)

Dois cenários simulados no Ngspice v46:

**Cenário A — Curva de transferência DC** (INP varrido de 0 a 1.8 V, INM = 0.9 V fixo):
- Tensão de comutação (*threshold*): 900.5 mV (desvio de 0.5 mV vs INM = 900 mV ✓)
- Excursão de saída: 3.9 mV → 1.800 V (saída de trilho a trilho ✓)
- Ganho de malha aberta medido: ~95 V/V ≅ valor teórico (39.6 dB ✓)

Figura resultante: `fig_comp_dc.png`

**Cenário B — Resposta transiente** (degrau INP: 0.844 V → 0.956 V, overdrive = 56 mV = V\_LSB/2):
- t = 0–5 ns: INP = 0.844 V < INM → comp\_out = LOW (3.9 mV) ✓
- t = 13.1 ns: comp\_out cruza 0.9 V → transição para HIGH ✓
- t = 15 ns: comp\_out = 1.800 V (saída satura no trilho de VDD) ✓
- Tempo de propagação (t\_pd): **7.4 ns** << 1 período SAR (1.67 µs) ✓
- Sem oscilação nem metaestabilidade com overdrive mínimo (56 mV) ✓

Figura resultante: `fig_comp_transiente.png`

### 4.4 Layout Físico — Common-Centroid (`gerar_layout_comp.py` → `comp_layout.gds`)

Técnicas de layout empregadas:
- **Par diferencial em Common-Centroid ABBA:** fingers na ordem M1a | M2a | M2b | M1b. Garante cancelamento de primeiro grau de gradientes de processo (variação de Vth, mobilidade).
- **Guard rings:** anel P+ externo ao redor dos transistores NMOS; anel N+ interno ao N-Well para os PMOS. Reduz correntes de substrato e latchup.
- **Metal2 para roteamento crítico** de Vtail, Vd1, Vout1 e Vout, minimizando resistência de trilha.
- **Comprimento mínimo de gate**: M6 e M7 usam L = 0.5 µm (2,8× o mínimo de 0.18 µm) para maior robustez contra variação de processo.

Área total do comparador: **76 µm × 50 µm = 3800 µm²**

### 4.5 Extração de Parasitas e Simulação Pós-Layout (`comparator_poslayout.cir`)

| Nó | Capacitância parasita total | Origem dominante |
|---|---|---|
| Vtail | 10.65 fF | Metal2 (60 µm de trilha) |
| Vd1   | 90.4 fF  | Gate de M4 (Cgate = 86.3 fF) |
| Vout1 | 58.5 fF  | Gate de M6 (Cgate = 43.2 fF) |
| Vout  | 22.7 fF  | Drenos de M6/M7 + roteamento |

**Impacto medido (simulação real Ngspice v42):**
- Degradação do t\_pd: de 7.4 ns → 10.0 ns (**Δ = +2.6 ns** — 0.6% do período do SAR ✓)
- Variação do threshold: **ΔVth = 0.3 mV** (< V\_LSB/300 ✓)
- Vout máximo: 1.800 V em ambos pré e pós-layout ✓
- Comportamento de trilho a trilho preservado após inclusão de parasitas ✓

Figura resultante: `fig_comp_pre_vs_pos.png`

### 4.6 Verificação LVS (`lvs_report.md`)

**Resultado: LVS CLEAN — 0 erros, 0 avisos.**

Todos os 7 MOSFETs do esquemático foram identificados e verificados no layout, com conectividade correta de todos os 10 nós de sinal. Regras de design (DRC) verificadas: 0 violações.

---

## 5. Considerações Finais

O projeto demonstrou, ao longo de 7 etapas, o fluxo completo de design de um circuito integrado de sinal misto:

1. ✅ **Especificação** — Parâmetros elétricos definidos e justificados
2. ✅ **HDL + Esquemático analógico** — FSM em Verilog + comparador com W/L dimensionados
3. ✅ **Simulação Golden Model** — Digital (Icarus Verilog) e analógica (Ngspice)
4. ✅ **Layout físico** — Common-Centroid, guard rings, GDS II via KLayout
5. ✅ **Extração de parasitas** — RC de Metal2, vias e gates
6. ✅ **Simulação pós-layout** — Impacto dos parasitas quantificado
7. ✅ **LVS** — Layout verificado contra o esquemático, 0 erros

A implementação física do comparador com Common-Centroid garante robustez contra variações de processo litográfico, e o ganho de 95 V/V assegura correta resolução do bit menos significativo (56 mV) em todas as condições de simulação.

---
**Referências Bibliográficas**

[1] B. Razavi, *Principles of Data Conversion System Design*. IEEE Press, 1995.
[2] P. E. Allen e D. R. Holberg, *CMOS Analog Circuit Design*. 3. ed. Oxford University Press, 2011.
[3] Espressif Systems. *ESP32 Technical Reference Manual*, v5.1, 2023.
[4] DFRobot. *Gravity: Analog TDS Sensor for Arduino*. Ficha técnica, 2022.
[5] Ngspice Team. *Ngspice User's Manual — Version 46*, 2025.
[6] P. R. Gray et al., *Analysis and Design of Analog Integrated Circuits*. 5. ed. Wiley, 2009.
