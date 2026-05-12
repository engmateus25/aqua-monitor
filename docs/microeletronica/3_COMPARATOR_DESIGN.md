# Etapa 2 (Analógico): Projeto do Comparador de Tensão — SAR ADC

**Bloco:** Comparador Diferencial de 2 Estágios (Open-Loop)
**Tecnologia:** CMOS 180nm | VDD = 1.8V | I_tail = 20µA

---

## 1. Justificativa da Arquitetura

O comparador é o único bloco puramente analógico do SAR ADC. Sua função é responder à
pergunta binária: "A tensão no nó `Vtop` do DAC é maior ou menor que a referência?"
A arquitetura escolhida é o **par diferencial PMOS com espelho de corrente NMOS + inversor
CMOS de saída**, padrão industrial para SAR ADCs de baixo consumo por três razões:

1. **Par PMOS:** permite que a entrada opere próxima ao GND (range de entrada estende-se
   até 0V para VDD = 1.8V e Vtp = 0.5V), cobrindo a excursão completa do `Vtop`.
2. **Carga espelho ativa:** converte saída diferencial em single-ended com ganho de tensão
   máximo: `A1 = gm · (rds_M2 || rds_M4)`.
3. **Inversor CMOS (estágio 2):** saída de trilho a trilho (0 a 1.8V), compatível com a
   FSM digital, sem nível de tensão intermediário.

---

## 2. Esquemático e Conexões

```
              VDD (1.8V)
               |
          ┌──[M5]──┐   ← Fonte de corrente de cauda PMOS (Vbias = 1.0V)
          │  Vtail  │
      ┌───┴───┐ ┌───┴───┐
    [M1]     [M2]        ← Par diferencial PMOS
   INM(ref) INP(sinal)
      │         │
     Vd1      Vout1 ────────────┐
      │         │               │
    [M3]      [M4]         [M7 PMOS] ← Carga ativa estágio 2
  (diodo)   (espelho)           │  (Gate=Vbias2=1.4V, Src=VDD)
      │         │            [Vout] ←── comp_out
     GND       GND           [M6 NMOS] ← Amplificador CS estágio 2
                                │  (Gate=Vout1, Src=GND)
                               GND
```

**Regra de polaridade (verificada por análise nodal):**
- INP ↑ → M2 menos ligado → I_M2 ↓, I_M1 ↑ → Vd1 ↑ → I_M4 ↑ → Vout1 ↓ → comp_out ↑ = **1**
- INP ↓ → trajetória inversa → comp_out = **0**

Portanto: `comp_out = 1` quando `INP > INM`, conforme exige a FSM SAR.

---

## 3. Dimensionamento dos Transistores (W/L)

### Parâmetros CMOS 180nm (Educational):
| Parâmetro | NMOS | PMOS |
|---|---|---|
| µ·Cox (µA/V²) | 270 | 90 |
| Vth (V) | +0.5 | −0.5 |
| λ (V⁻¹, L=1µm) | 0.10 | 0.10 |
| TOX (nm) | 4 | 4 |

### Tabela de Dimensionamento:

| Transistor | Tipo | W (µm) | L (µm) | W/L | Função | I_D (µA) | V_ov (V) |
|---|---|---|---|---|---|---|---|
| **M1** | PMOS | 20 | 1.0 | 20 | Par diferencial (−) / INM | 10 | 0.105 |
| **M2** | PMOS | 20 | 1.0 | 20 | Par diferencial (+) / INP | 10 | 0.105 |
| **M3** | NMOS | 10 | 1.0 | 10 | Espelho de corrente (ref, diodo) | 10 | 0.086 |
| **M4** | NMOS | 10 | 1.0 | 10 | Espelho de corrente (cópia) | 10 | 0.086 |
| **M5** | PMOS | 10 | 2.0 | 5  | Fonte de corrente de cauda | 20 | 0.298 |
| **M6** | NMOS | 10 | 0.5 | 20 | Amplificador common-source | — | — |
| **M7** | PMOS | 20 | 0.5 | 40 | Carga ativa estágio 2 | — | — |

### Cálculos de Verificação:

**M5 (Tail Current Source):**
```
I_tail = (1/2) · µpCox · (W/L) · V_ov²
20µA = (1/2) · 90µA/V² · 5 · V_ov²
V_ov = sqrt(20e-6 / 225e-6) = 0.298 V
Vbias_M5 = VDD − |Vtp| − V_ov = 1.8 − 0.5 − 0.298 = 1.002 V ≈ 1.0 V ✓
```

**M1, M2 (Differential Pair):**
```
I_D = 10µA (I_tail / 2)
V_ov = sqrt(2 · I_D / (µpCox · W/L)) = sqrt(2·10e-6 / (90e-6·20)) = 0.105 V
gm = 2 · I_D / V_ov = 2 · 10µA / 0.105V = 190 µA/V
```

**Ganho do Estágio 1 (A₁):**
```
rds_M2 = 1 / (λp · I_D) = 1 / (0.1 · 10µA) = 1 MΩ
rds_M4 = 1 / (λn · I_D) = 1 / (0.1 · 10µA) = 1 MΩ
Rout1  = rds_M2 || rds_M4 = 500 kΩ
A₁     = gm · Rout1 = 190µA/V · 500kΩ = 95 V/V = 39.6 dB
```
**Requisito atendido:** A₁ = 95 V/V >> A_min = 32 V/V (30 dB) para resolver V_LSB/2 = 56 mV ✓

**M7 (PMOS Current Source, Stage 2):**
```
Vbias2 = 1.4V → Vgs_M7 = 1.4 − 1.8 = −0.4V → V_ov = |Vgs| − |Vtp| = 0.4 − 0.5 < 0
→ Ajuste: Vbias2 = 1.2V → Vgs_M7 = −0.6V → V_ov = 0.1V
I_D7 = (1/2)·90e-6·40·0.01 = 18 µA ≈ 20 µA ✓
```

---

## 4. Tensões de Polarização

| Sinal | Valor | Descrição |
|---|---|---|
| VDD | 1.8 V | Alimentação |
| Vbias | 1.0 V | Gate de M5 (tail PMOS) |
| Vbias2 | 1.2 V | Gate de M7 (load PMOS, estágio 2) |
| INM | 0.9 V | Entrada de referência (VREF/2) |
| INP | variável | Entrada de sinal (DAC Vtop + 0.9V) |

---

## 5. Próximos Passos
- Etapa 3: Simulação pré-layout (`comparator_prelayout.cir`) — curva de transferência DC + resposta transiente
- Etapa 4: Layout Common-Centroid no KLayout (`gerar_layout_comp.py`)
- Etapa 5: Extração de parasitas + simulação pós-layout (`comparator_poslayout.cir`)
- Etapa 7: Verificação LVS (`lvs_report.md`)
