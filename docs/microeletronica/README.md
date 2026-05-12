# Documentação do Projeto de Microeletrônica — SAR ADC de 4-Bits

**Disciplina:** Design de Circuitos Integrados — Unidade 7 | Capítulo 5
**Professor:** João Fonseca
**Autor:** Matheus Serrão Uchôa | Matrícula: 22052633

---

## 📌 O que era para ser feito (Enunciado)

O desafio consistia em projetar um circuito integrado de **livre escolha**, passando pelo fluxo completo de design de chips:

1. **Descrição do Circuito** — especificações técnicas
2. **Esquemático ou HDL** — Verilog/VHDL para digital; transistores (W/L) para analógico
3. **Simulação Funcional (Golden Model)** — validar antes do layout
4. **Layout do Circuito** — implementação física com DRC
5. **Extração de Parasitas** — capacitâncias e resistências das trilhas
6. **Simulação Pós-Layout** — comparar com o Golden Model
7. **LVS (Layout vs. Schematic)** — verificar correspondência física

O relatório final deveria ser formatado como **Technical Paper** com: Introdução, Metodologia, Resultados (prints de todas as etapas), Análise Crítica e Referências.

---

## ✅ O que foi feito (Resultados)

### Etapa 1 — Especificação do Circuito ✅
- **Circuito escolhido:** SAR ADC de 4-bits (Mixed-Signal) para os sensores de Turbidez e TDS do Aqua Monitor
- **Justificativa:** O ADC interno do ESP32 sofre interferência do rádio Wi-Fi. Um ADC customizado com layout controlado resolve o problema
- **Arquivo:** `1_SPECIFICATION.md`

**Especificações definidas:**

| Parâmetro | Valor |
|---|---|
| Tecnologia | CMOS 180nm |
| Alimentação ($V_{DD}$) | 1.8 V |
| Resolução | 4 bits (16 níveis) |
| $V_{LSB}$ | 112.5 mV |
| Capacitor unitário ($C_0$) | 100 fF |
| Capacitância total | 1.6 pF |
| Frequência de amostragem | 100 kS/s |

---

### Etapa 2 — HDL (Verilog RTL) ✅
- FSM de 7 estados implementada: `IDLE → SAMPLE → BIT3 → BIT2 → BIT1 → BIT0 → DONE`
- Testbench completo para validação automatizada
- **Arquivos:** `sar_fsm_4bit.v`, `tb_sar_fsm.v`

---

### Etapa 3 — Simulação Funcional Digital ✅
- Simulador: **Icarus Verilog v12** (execução via terminal)
- Resultado: **SUCESSO** — conversão correta de `Vin ≈ 1.125V` para `1010₂` (decimal 10)

**Log real do terminal:**
```
Time: 45ns | State: BIT3  | comp_out: 1 | dac_in: 1100  (mantém MSB)
Time: 65ns | State: BIT2  | comp_out: 0 | dac_in: 1010  (rejeita b2)
Time: 75ns | State: BIT1  | comp_out: 1 | dac_in: 1011  (mantém b1)
Time: 95ns | State: DONE  | eoc: 1      | data_out: 1010 ✅
SUCESSO: A conversão terminou corretamente. Resultado = 1010
```

---

### Etapa 3b — Simulação Funcional Analógica (DAC SPICE) ✅
- Simulador: **Ngspice v46** (execução via terminal)
- Circuito: rede de 5 capacitores (8C, 4C, 2C, 1C, 1C) com chave S&H ideal
- Resultado gerado: `dac_sim.raw` (764 pontos temporais, passo de 10ns)
- **Arquivo:** `dac_4bit.cir`

**Resultados extraídos do `dac_sim.raw`:**

| Instante | Fase | $V_{top}$ Teórico | $V_{top}$ Simulado | Erro |
|---|---|---|---|---|
| 1.00 µs | SAMPLE | -1.250 V | -1.250 V | <0.01% |
| 2.01 µs | BIT3 ativo | +0.650 V | +0.648 V | 0.31% |
| 5.01 µs | BIT1 ativo | +0.612 V | +0.616 V | 0.65% |

---

### Etapas 4–7 — Layout / Extração / LVS ⏳ (Previstas)
- Ferramenta instalada: **KLayout v0.30.8**
- Técnica planejada: **Common-Centroid** para os 16 capacitores MIM
- Área estimada: ~40 µm × 40 µm = 1600 µm²
- Estas etapas constituem a continuação natural do projeto

---

## 🔧 Dificuldades Técnicas Encontradas e Soluções

| # | Dificuldade | Solução |
|---|---|---|
| 1 | Nó flutuante em SPICE (singularidade numérica na fase HOLD) | Inserção de $R_{leak} = 1\,\text{T}\Omega$ entre $V_{top}$ e GND |
| 2 | Falha de co-simulação AMS (Verilog + SPICE) | Desacoplamento dos domínios: FSM validada separadamente do DAC |
| 3 | Caracteres UTF-8 incompatíveis no compilador LaTeX | Reescrita com equivalentes ASCII e macros LaTeX |

---

## 📂 Estrutura desta Pasta

```
docs/microeletronica/
├── README.md                  ← Este arquivo (visão geral)
├── 1_SPECIFICATION.md         ← Especificações técnicas formais
├── 2_ANALOG_DESIGN.md         ← Cálculos do DAC (kT/C, dimensionamento)
├── sar_fsm_4bit.v             ← Código Verilog RTL da FSM SAR
├── tb_sar_fsm.v               ← Testbench Verilog
├── sar_fsm_sim.vvp            ← Binário compilado da simulação
├── dac_4bit.cir               ← Netlist SPICE do banco capacitivo
├── dac_sim.raw                ← Vetores de saída da simulação SPICE (Ngspice)
├── RELATORIO_FINAL.md         ← Relatório resumido em Markdown
├── relatorio_sar_adc.tex      ← Relatório completo em LaTeX (nível doutorado)
├── relatorio_sar_adc.pdf      ← PDF compilado do relatório
└── images/                    ← Fotos dos sensores usadas no relatório
    ├── Home-inicial.png
    ├── circuito_simulado.jpeg
    ├── ckt_completo.jpg
    ├── pH.jpg
    ├── turbidez.jpg
    ├── condutividade.jpg
    ├── temperatura.jpg
    └── coleta.jpg
```

---

## 🛠️ Ferramentas Utilizadas

| Ferramenta | Versão | Uso | Licença |
|---|---|---|---|
| Icarus Verilog | v12 (2022) | Compilação e simulação RTL | GPL |
| Ngspice | v46 (2025) | Simulação SPICE analógica | BSD |
| KLayout | v0.30.8 | Layout físico (etapa futura) | GPL |
| Tectonic | v0.15.0 | Compilação LaTeX → PDF | MIT |

---

## 📚 Referências

1. RAZAVI, B. *Principles of Data Conversion System Design*. IEEE Press, 1995.
2. ALLEN, P. E.; HOLBERG, D. R. *CMOS Analog Circuit Design*. 3. ed. Oxford, 2011.
3. ESPRESSIF SYSTEMS. *ESP32 Technical Reference Manual*. v5.1, 2023.
4. DFROBOT. *Gravity: Analog TDS Sensor for Arduino*. Ficha técnica, 2022.
5. NGSPICE TEAM. *Ngspice User's Manual — Version 46*. 2025.
